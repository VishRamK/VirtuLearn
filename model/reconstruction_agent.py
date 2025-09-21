#!/usr/bin/env python3
# scripts/augment_transcript.py

import os
import json
import asyncio
import re
from typing import List, Optional, Dict, Any
from pathlib import Path

from dotenv import load_dotenv
from agents import Agent, Runner

# --- CONFIG: set your input/output paths here ---
# NOTE: fix the filename if yours is "transcript.txt" (your repo uses "trasncript.txt")
transcript_path = Path("DL_lec2.txt")
out_path = Path("augmented_transcript.txt")
NUM_CHUNKS = 5
OVERLAP_LINES = 8
# ------------------------------------------------

def ensure_env():
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not found. Add it to your .env or environment.")
    return key

def read_transcript(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Transcript not found: {path}")
    return path.read_text(encoding="utf-8")

def split_into_n_chunks_by_lines(text: str, n: int = 5, overlap: int = 8) -> List[Dict[str, Any]]:
    lines = text.splitlines()
    total = len(lines)
    if n <= 0 or n > total:
        return [{"index": 0, "start": 0, "end": total, "text": text}]
    base = total // n
    rem = total % n

    chunks = []
    start = 0
    for i in range(n):
        length = base + (1 if i < rem else 0)
        end = start + length
        s = max(0, start - (overlap if i > 0 else 0))
        e = min(total, end + (overlap if i < n - 1 else 0))
        chunk_text = "\n".join(lines[s:e])
        chunks.append({"index": i, "start": s, "end": e, "text": chunk_text})
        start = end
    return chunks

# Agent that returns insert directives for augmentation
question_reconstructor = Agent(
    name="Question Reconstructor (Chunk)",
    instructions=(
        "You analyze a lecture transcript chunk recorded from the instructor’s mic only. "
        "Student questions may be missing.\n\n"
        "You will be given BASE_LINE_START (absolute line index of this chunk’s first line in the FULL transcript) "
        "and the TRANSCRIPT CHUNK.\n\n"
        "Tasks:\n"
        "1) Identify points where the instructor’s utterance implies they are responding to a student question "
        "(e.g., 'Great question…', 'To answer that…', 'No, actually…', abrupt answers, or answer-like structures).\n"
        "2) For each such point, reconstruct the most likely student question (short, natural question).\n"
        "3) Provide teacher evidence (quotes from instructor lines that led you to infer the question).\n"
        "4) Provide a short rationale and a confidence score (0.0–1.0).\n"
        "5) IMPORTANT: Provide insert directives with absolute line numbers in the FULL transcript:\n"
        "   - absolute_line = BASE_LINE_START + local_line_index_in_chunk\n"
        "   - Insert AFTER the evidence line unless a BEFORE insert is clearly more sensible; indicate via flag.\n\n"
        "Return ONLY valid JSON with this exact schema:\n"
        "{\n"
        '  "summary": {\n'
        '    "num_reconstructed": number,\n'
        '    "notes": "short notes about patterns observed"\n'
        "  },\n"
        '  "missing_questions": [\n'
        "    {\n"
        '      "location_hint": "absolute line number or short description",\n'
        '      "teacher_evidence": ["quotes from instructor lines in this chunk"],\n'
        '      "inferred_question": "short direct question",\n'
        '      "rationale": "why this question is likely",\n'
        '      "confidence": 0.0,\n'
        '      "insert_directive": {\n'
        '        "absolute_line": number,\n'
        '        "insert_after": true\n'
        "      }\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Do not include any text outside the JSON."
    ),
)

def make_chunk_prompt(chunk: Dict[str, Any]) -> str:
    base_line_start = chunk["start"]
    return f"""
[BASE_LINE_START]
{base_line_start}

[TRANSCRIPT CHUNK]
{chunk["text"]}

Follow your instructions and output ONLY the JSON.
"""

async def run_chunk(chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
    prompt = make_chunk_prompt(chunk)
    result = await Runner.run(question_reconstructor, prompt)
    raw = result.final_output
    try:
        data = json.loads(raw)
        return data.get("missing_questions", [])
    except Exception:
        # print(f"[warn] Malformed JSON for chunk {chunk['index']}: {raw}")
        return []

# --- Merger utilities ---
def _parse_first_int(s: str) -> Optional[int]:
    if not s:
        return None
    m = re.search(r"(\d+)", s)
    return int(m.group(1)) if m else None

def _find_index_by_evidence(lines: List[str], evidence: List[str]) -> Optional[int]:
    for ev in evidence or []:
        ev_clean = ev.strip()
        if not ev_clean:
            continue
        for i, ln in enumerate(lines):
            if ln.strip() == ev_clean:
                return i
        for i, ln in enumerate(lines):
            if ev_clean in ln:
                return i
    return None

def merge_questions_into_transcript(
    transcript: str,
    reconstructed: List[Dict[str, Any]],
    insert_after_default: bool = True,
    add_lecturer_tag: bool = False,
    location_hint_is_one_based: bool = False,  # using 0-based absolute_line
    include_evidence_line: bool = True,
) -> str:
    lines = transcript.splitlines()
    augmented = list(lines)
    offset = 0

    # Normalize into (target_idx, data)
    targets = []
    for item in reconstructed:
        data = dict(item)
        ins = data.get("insert_directive") or {}
        idx = ins.get("absolute_line", None)

        if idx is None:
            loc = _parse_first_int(data.get("location_hint") or "")
            if loc is not None:
                if location_hint_is_one_based:
                    loc = max(1, loc) - 1
                idx = max(0, min(len(lines) - 1, loc))
            else:
                idx = _find_index_by_evidence(lines, data.get("teacher_evidence") or [])
                if idx is None:
                    idx = len(lines) - 1

        targets.append((idx, data))

    targets.sort(key=lambda t: t[0])

    for base_idx, data in targets:
        item_insert_after = insert_after_default
        ins = data.get("insert_directive") or {}
        if "insert_after" in ins:
            item_insert_after = bool(ins["insert_after"])

        insert_idx = base_idx + offset + (1 if item_insert_after else 0)
        insert_idx = max(0, min(len(augmented), insert_idx))

        q = (data.get("inferred_question") or "").strip()
        conf = float(data.get("confidence") or 0.0)

        augmented.insert(insert_idx, f"[STUDENT] (reconstructed, confidence={conf:.2f}): {q}")
        offset += 1
        insert_idx += 1

        if include_evidence_line:
            evid_list = data.get("teacher_evidence") or []
            if evid_list:
                ev = evid_list[0].strip()
                if ev:
                    augmented.insert(insert_idx, f"[EVIDENCE] {ev}")
                    offset += 1
                    insert_idx += 1

    if add_lecturer_tag:
        for i, ln in enumerate(augmented):
            if ln.startswith("Teacher:") and not ln.startswith("[LECTURER]"):
                augmented[i] = f"[LECTURER] {ln}"

    return "\n".join(augmented)
# --- end Merger utilities ---

async def main() -> None:
    ensure_env()
    transcript = read_transcript(transcript_path)

    # Chunk and run in parallel
    chunks = split_into_n_chunks_by_lines(transcript, n=NUM_CHUNKS, overlap=OVERLAP_LINES)
    results = await asyncio.gather(*[run_chunk(c) for c in chunks])

    # Flatten + dedupe
    missing_questions_flat = [item for sub in results for item in sub]
    seen = set()
    deduped = []
    for mq in missing_questions_flat:
        abs_line = None
        if mq.get("insert_directive") and "absolute_line" in mq["insert_directive"]:
            abs_line = mq["insert_directive"]["absolute_line"]
        key = (abs_line, (mq.get("inferred_question") or "").strip().lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(mq)

    augmented_text = merge_questions_into_transcript(
        transcript=transcript,
        reconstructed=deduped,
        insert_after_default=True,
        add_lecturer_tag=False,
        location_hint_is_one_based=False,  # absolute_line is 0-based
        include_evidence_line=True,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(augmented_text, encoding="utf-8")
    print(f"[ok] Wrote augmented transcript: {out_path.resolve()}")

if __name__ == "__main__":
    asyncio.run(main())
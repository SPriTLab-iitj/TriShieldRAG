# """
# backends_status.py — ping each LLM backend and show which are live.
# Run:  DEMO_MODE=0 .venv/bin/python3.11 backends_status.py
# Use this right before the demo so you KNOW what Ring 3 will use.
# """
# import os, sys, time
# from pathlib import Path
# sys.path.insert(0, str(Path(__file__).resolve().parent))

# try:
#     from dotenv import load_dotenv; load_dotenv()
# except Exception:
#     pass


# def check(name, fn):
#     t0 = time.time()
#     try:
#         out = fn()
#         ms = int((time.time() - t0) * 1000)
#         print(f"  [LIVE] {name:22} -> {str(out).strip()[:30]!r}  ({ms} ms)")
#         return True
#     except Exception as e:
#         msg = str(e).splitlines()[0][:70]
#         print(f"  [DOWN] {name:22} -> {msg}")
#         return False


# def claude():
#     from anthropic import Anthropic
#     r = Anthropic().messages.create(
#         model="claude-haiku-4-5", max_tokens=5,
#         messages=[{"role": "user", "content": "say OK"}])
#     return r.content[0].text


# def mistral():
#     key = os.getenv("MISTRAL_API_KEY")
#     if not key:
#         raise RuntimeError("MISTRAL_API_KEY not set (skipped)")
#     from mistralai import Mistral as MistralClient
#     c = MistralClient(api_key=key)
#     r = c.chat.complete(
#         model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
#         max_tokens=5,
#         messages=[{"role": "user", "content": "say OK"}])
#     return r.choices[0].message.content


# def ollama():
#     from openai import OpenAI
#     c = OpenAI(
#         base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
#         api_key="ollama")
#     r = c.chat.completions.create(
#         model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
#         max_tokens=5,
#         messages=[{"role": "user", "content": "say OK"}])
#     return r.choices[0].message.content


# if __name__ == "__main__":
#     demo = os.getenv("DEMO_MODE", "1") not in ("0", "false", "False")
#     print(f"\nDEMO_MODE={os.getenv('DEMO_MODE','1')}  ->  ", end="")
#     print("DEMO mode: Ring 3 uses 3 MOCK LLMs (no network)\n" if demo
#           else "LIVE mode: Ring 3 uses the live backends below\n")

#     print("Pinging backends:")
#     live = []
#     if check("Claude (Anthropic)",       claude):  live.append("Claude")
#     if check("Mistral-Small (MistralAI)", mistral): live.append("Mistral")
#     if check("Ollama (local Meta)",      ollama):  live.append("LLaMA")

#     print(f"\nLive backends : {live or 'none — run with DEMO_MODE=1'}")
#     print(f"Ring 3 panel  : {len(live)} vendor(s) active")

#     if not demo and len(live) < 2:
#         print("\nWARNING: Live mode wants >= 2 backends for real consensus.")
#         print("         Start Ollama or add another key, or use DEMO_MODE=1.")

#     if not demo and len(live) >= 2:
#         print("\nRing 3 vendor diversity:")
#         vendor_map = {
#             "Claude":  "Anthropic  (US, Constitutional AI)",
#             "Mistral": "Mistral AI (France, EU-trained)",
#             "LLaMA":   "Meta       (US, open-weight, local)",
#         }
#         for b in live:
#             print(f"  {b:8s} -> {vendor_map.get(b, 'unknown')}")
#         print("\n✅  Ready for demo. Run: DEMO_MODE=0 bash run_live.sh")



"""
backends_status.py — ping each LLM backend and show which are live.

Run for any of the three modes:
  DEMO_MODE=1 .venv/bin/python3.11 backends_status.py   (default/mock demo)
  DEMO_MODE=0 .venv/bin/python3.11 backends_status.py   (live demo, small KB)
  DEMO_MODE=2 .venv/bin/python3.11 backends_status.py   (scale mode, big KB)

Use this right before your demo/viva so you KNOW what Ring 3 will use.

NOTE: this script now imports its mode-detection logic directly from
ragshield_core.config, instead of recalculating it locally. This means
it automatically understands all THREE modes (0, 1, 2) and will never
drift out of sync with the rest of the app again.
"""
import os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass

# ── Import the SAME mode-detection functions the rest of the app uses,
#    instead of recalculating "is this demo mode?" locally. This is the
#    fix: previously this file had its own hardcoded copy of the old
#    2-mode logic, which never learned about DEMO_MODE=2 when Scale
#    Mode was added elsewhere. Importing directly means this script
#    can never drift out of sync with config.py again. ──
from ragshield_core import config


def check(name, fn):
    t0 = time.time()
    try:
        out = fn()
        ms = int((time.time() - t0) * 1000)
        print(f"  [LIVE] {name:22} -> {str(out).strip()[:30]!r}  ({ms} ms)")
        return True
    except Exception as e:
        msg = str(e).splitlines()[0][:70]
        print(f"  [DOWN] {name:22} -> {msg}")
        return False


def claude():
    from anthropic import Anthropic
    r = Anthropic().messages.create(
        model="claude-haiku-4-5", max_tokens=5,
        messages=[{"role": "user", "content": "say OK"}])
    return r.content[0].text


def mistral():
    key = os.getenv("MISTRAL_API_KEY")
    if not key:
        raise RuntimeError("MISTRAL_API_KEY not set (skipped)")
    from mistralai import Mistral as MistralClient
    c = MistralClient(api_key=key)
    r = c.chat.complete(
        model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
        max_tokens=5,
        messages=[{"role": "user", "content": "say OK"}])
    return r.choices[0].message.content


def ollama():
    from openai import OpenAI
    c = OpenAI(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        api_key="ollama")
    r = c.chat.completions.create(
        model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        max_tokens=5,
        messages=[{"role": "user", "content": "say OK"}])
    return r.choices[0].message.content


if __name__ == "__main__":
    raw_mode = os.getenv("DEMO_MODE", "1")

    # ── NEW: use config.py's actual functions, not a local recalculation ──
    is_demo  = config.demo_mode()
    is_scale = config.scale_mode()
    is_live  = (not is_demo) and (not is_scale)   # i.e. DEMO_MODE=0 exactly

    print(f"\nDEMO_MODE={raw_mode}  ->  ", end="")
    if is_scale:
        print("SCALE mode: Ring 3 uses LIVE backends against YOUR large "
              "dataset\n")
    elif is_demo:
        print("DEMO mode: Ring 3 uses 3 MOCK LLMs (no network)\n")
    else:
        print("LIVE mode: Ring 3 uses the live backends below "
              "(small built-in KB)\n")

    print("Pinging backends:")
    live = []
    if check("Claude (Anthropic)",       claude):  live.append("Claude")
    if check("Mistral-Small (MistralAI)", mistral): live.append("Mistral")
    if check("Ollama (local Meta)",      ollama):  live.append("LLaMA")

    print(f"\nLive backends : {live or 'none — run with DEMO_MODE=1'}")
    print(f"Ring 3 panel  : {len(live)} vendor(s) active")

    # ── FIXED: this warning/diversity block used to only ever check
    # "not demo", which was True for BOTH DEMO_MODE=0 and DEMO_MODE=2 —
    # meaning it couldn't tell the two apart. Now it checks is_live or
    # is_scale explicitly, and mentions which one you're actually in. ──
    if (is_live or is_scale) and len(live) < 2:
        print("\nWARNING: This mode wants >= 2 backends for real consensus.")
        print("         Start Ollama or add another key, or use DEMO_MODE=1.")

    if (is_live or is_scale) and len(live) >= 2:
        print("\nRing 3 vendor diversity:")
        vendor_map = {
            "Claude":  "Anthropic  (US, Constitutional AI)",
            "Mistral": "Mistral AI (France, EU-trained)",
            "LLaMA":   "Meta       (US, open-weight, local)",
        }
        for b in live:
            print(f"  {b:8s} -> {vendor_map.get(b, 'unknown')}")

        if is_scale:
            print("\n✅  Ready for scale testing. Run: DEMO_MODE=2 bash run_live.sh")
        else:
            print("\n✅  Ready for demo. Run: DEMO_MODE=0 bash run_live.sh")

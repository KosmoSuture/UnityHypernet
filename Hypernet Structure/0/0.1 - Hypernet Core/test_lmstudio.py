"""
LM Studio Connection Test
Run this from the '0.1 - Hypernet Core' directory to verify LM Studio is working.

Usage:
    python test_lmstudio.py
    python test_lmstudio.py --model local/llama-3.2-3b-instruct
"""
import sys
import argparse

sys.path.insert(0, ".")


def main():
    parser = argparse.ArgumentParser(description="Test LM Studio connection")
    parser.add_argument(
        "--model",
        default="local/qwen2.5-coder-7b-instruct",
        help="Model name with local/ prefix (default: local/qwen2.5-coder-7b-instruct)",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:1234/v1",
        help="LM Studio server URL (default: http://localhost:1234/v1)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  LM STUDIO CONNECTION TEST")
    print("=" * 60)
    print()

    # Step 1: Check if openai package is installed
    print("[1/4] Checking for openai package...")
    try:
        import openai

        print(f"      OK - openai {openai.__version__}")
    except ImportError:
        print("      FAIL - openai package not installed")
        print("      Fix: pip install openai")
        return False

    # Step 2: Check if LM Studio server is reachable
    print(f"[2/4] Checking LM Studio server at {args.url}...")
    try:
        import urllib.request
        import json

        req = urllib.request.Request(f"{args.url}/models")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            models = [m.get("id", "unknown") for m in data.get("data", [])]
            if models:
                print(f"      OK - Server running, models available: {models}")
            else:
                print("      WARN - Server running but no models loaded")
                print("      Fix: Load a model in LM Studio before testing")
                return False
    except Exception as e:
        print(f"      FAIL - Cannot reach server: {e}")
        print()
        print("      Troubleshooting:")
        print("      1. Is LM Studio running?")
        print("      2. Go to Local Server tab -> click 'Start Server'")
        print("      3. Make sure a model is loaded (Models tab)")
        print(f"      4. Check the server is on the right port ({args.url})")
        return False

    # Step 3: Test via LMStudioProvider
    print(f"[3/4] Testing LMStudioProvider with model '{args.model}'...")
    try:
        from hypernet.providers import LMStudioProvider

        provider = LMStudioProvider(base_url=args.url)
        response = provider.complete(
            model=args.model,
            system="You are a helpful librarian. Respond in one sentence.",
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Please confirm you can hear me by describing your purpose in one sentence.",
                }
            ],
            max_tokens=150,
        )
        print(f"      OK - Response received ({response.tokens_used} tokens)")
        print(f"      Response: {response.text[:200]}")
    except Exception as e:
        print(f"      FAIL - Provider error: {e}")
        print()
        print("      Troubleshooting:")
        print(f"      - Model name '{args.model}' may not match LM Studio's model ID")
        print("      - Check http://localhost:1234/v1/models for exact model names")
        print("      - Try: python test_lmstudio.py --model local/<exact-model-id>")
        return False

    # Step 4: Test swarm config detection
    print("[4/4] Testing swarm config model routing...")
    try:
        from hypernet.providers import detect_provider_class, LMStudioProvider as LSP

        cls = detect_provider_class(args.model)
        if cls == LSP:
            print(f"      OK - '{args.model}' correctly routes to LMStudioProvider")
        else:
            print(
                f"      WARN - '{args.model}' routes to {cls.__name__ if cls else 'None'}"
            )
            print("      Fix: Model name must start with 'local/' or 'lmstudio/'")
    except Exception as e:
        print(f"      WARN - Could not test routing: {e}")

    print()
    print("=" * 60)
    print("  ALL TESTS PASSED - LM Studio is ready for the swarm!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Start the swarm:")
    print('     python -m hypernet.swarm --archive "../.." --config secrets/config.json')
    print()
    print("  2. Or test in mock mode first:")
    print(
        '     python -m hypernet.swarm --mock --archive "../.." --config secrets/config.json'
    )
    print()
    print("  3. Check status:")
    print("     python -m hypernet.swarm --status")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

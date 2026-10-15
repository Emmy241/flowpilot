from app.services.llm import run_llm

print("=== Test 1: plain chat ===")
r1 = run_llm([{"role": "user", "content": "Say hello in one short sentence."}])
print(r1)

print("\n=== Test 2: task intent ===")
r2 = run_llm([{"role": "user", "content": "Remind me to call mom tomorrow at 6pm"}])
print(r2)

print("\n=== Test 3: ambiguous ===")
r3 = run_llm([{"role": "user", "content": "What's the weather like?"}])
print(r3)

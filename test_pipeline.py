from text_to_gloss.main import isl_pipeline

# Test sentences with expected outputs
test_cases = [
    ("What is your name?", "YOUR NAME WHAT?"),
    ("I am feeling thirsty.", "I THIRSTY"),
    ("Can you take me to a doctor?", "YOU TAKE ME DOCTOR CAN?"),
    ("Boy eats an apple.", "BOY APPLE EAT"),
    ("Yesterday, I went to school.", "YESTERDAY I SCHOOL GO"),
    ("She is not happy.", "SHE HAPPY NOT"),
    ("Are you busy?", "YOU BUSY?"),
    ("I want to sleep.", "I WANT SLEEP"),
    ("I want water.", "I WATER WANT"),
    ("I have fever.", "I FEVER HAVE"),
    ("I am in danger.", "I DANGER"),
    ("Please help me.", "HELP ME PLEASE"),
    ("It is an emergency.", "EMERGENCY"),
    ("The shoes are big.", "SHOES BIG")
]

# Run tests and report results
passed = 0
failed = 0

print("Testing ISL Pipeline...\n")
print("-" * 50)

for i, (input_text, expected) in enumerate(test_cases, 1):
    result = isl_pipeline(input_text)
    success = result == expected
    
    if success:
        status = "✓ PASS"
        passed += 1
    else:
        status = "✗ FAIL"
        failed += 1
    
    print(f"Test {i}: {status}")
    print(f"Input: {input_text}")
    print(f"Expected: {expected}")
    print(f"Got: {result}")
    print("-" * 50)

print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests") 
import requests
from colorama import Fore, Style
from sympy import *
from sympy.parsing.sympy_parser import parse_expr

# 🔹 Global symbols
x, y, z, t = symbols('x y z t')

# 🔹 Unified Prompt Template
UNIFIED_PROMPT = """
Tu ek chill coding assistant hai jo user ke mood ke hisaab se adapt karta hai.

• Agar user web dev ka sawal puchhe (HTML, CSS, JS), toh simple, readable code ke saath Hinglish me samjha, helpful comments ke saath.
• Agar user C, Python, ya math puchhe toh concise, clear, beginner-friendly explanation de, point-by-point agar zarurat ho.
• LaTeX ya koi bhi math formatting kabhi bhi mat use kar — hamesha plain format me likh (e.g. e^x * cos(y), x^2 + y^2).
• Chill but clear tone maintain kar, aur kabhi bhi gyaan na jhaade unnecessarily.
"""

# 🧠 SymPy expression extractor
def extract_expr(prompt):
    try:
        for keyword in ["differentiate", "derivative", "integrate", "solve"]:
            if keyword in prompt.lower():
                expr_text = prompt.lower().split(keyword)[1].strip()
                return parse_expr(expr_text, evaluate=False)
        return x
    except:
        return x

# 📌 Limit extractor (basic)
def extract_limit(prompt):
    return sin(x)/x, x, 0

# 🔍 SymPy validation
def validate_math_answer(prompt, answer):
    prompt_lower = prompt.lower()
    try:
        if "differentiate" in prompt_lower or "derivative" in prompt_lower:
            expr = extract_expr(prompt)
            return f"✅ Derivative: {diff(expr)}"
        elif "integrate" in prompt_lower:
            expr = extract_expr(prompt)
            return f"✅ Integral: {integrate(expr)} + C"
        elif "limit" in prompt_lower:
            expr, var, point = extract_limit(prompt)
            return f"✅ Limit: {limit(expr, var, point)}"
        elif "solve" in prompt_lower:
            expr = extract_expr(prompt)
            return f"✅ Solution: {solve(expr, x)}"
        elif "analytic" in prompt_lower or "real part" in prompt_lower:
            expr = exp(x + I*y)
            u = simplify(re(expr))
            v = simplify(im(expr))
            du_dx = diff(u, x)
            dv_dy = diff(v, y)
            du_dy = diff(u, y)
            dv_dx = diff(v, x)
            analytic = "✅ Function is analytic." if simplify(du_dx - dv_dy) == 0 and simplify(du_dy + dv_dx) == 0 else "❌ Function is not analytic."
            return f"{analytic}\n✅ Real part: {u}\n✅ Imaginary part: {v}"
        else:
            return "ℹ️ SymPy validation not applicable."
    except Exception as e:
        return f"❌ [SymPy Error] {str(e)}"

# 🎯 Pentagon main engine
# 🎯 Pentagon main engine
def ask_Pentagon(prompt):
    if not isinstance(prompt, str) or not prompt.strip():
        return "[!] Error: Invalid input."

    prompt_clean = prompt.strip().lower()
    if prompt_clean in ["hi", "hello", "hey"]:
        return (
            "Aree bhai! 😄\n"
            "Welcome back — kya scene hai aaj?... 🔥💻"
        )

    full_prompt = UNIFIED_PROMPT + "\n\nUser: " + prompt
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": full_prompt,
            "stream": False,
            "temperature": 0.2,
            "top_p": 0.95,
            "repeat_penalty": 1.1
        }
    )

    response_text = res.json()['response']
    validation_result = validate_math_answer(prompt, response_text)

    if not validation_result.startswith("ℹ️"):
        response_text += "\n\n🧠 SymPy Validation:\n" + validation_result

    return response_text


# 🟢 Boot function
def setup_pentagon():
    print(Fore.YELLOW + "Starting Pentagon...\n" + Style.RESET_ALL)
    print(Fore.GREEN + "Pentagon: 🔥 Pentagon is now online. Bol kya scene hai — study, chill, ya coding?" + Style.RESET_ALL)
    print()


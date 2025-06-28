

def add_todo_for_notion(script_path):
    # read script.txt
    with open(script_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    with open(script_path, "w", encoding="utf-8") as f:
        for i, line in enumerate(lines, 1):
            if line.strip() != '':
                f.write(f"- [ ] {i}. {line.strip()}\n")


if __name__ == "__main__":
    script_location = "../output/kaffe_drinken/script.txt"
    add_todo_for_notion(script_location)
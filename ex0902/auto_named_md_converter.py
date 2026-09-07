import os
import sys
import json
from pathlib import Path
import argparse

def create_markdown_template(directory_path, overwrite=False):
    target_dir = Path(directory_path).resolve()
    current_script_path = Path(__file__).resolve()
    
    if not target_dir.is_dir():
        print(f"오류: '{target_dir}'은(는) 유효한 디렉터리가 아닙니다.")
        sys.exit(1)

    output_filename = f"{target_dir.name}.md"
    out_file = target_dir / output_filename
    
    # 이미 파일이 존재하는지 검사
    if out_file.exists() and not overwrite:
        print(f"알림: '{out_file.name}' 파일이 이미 존재합니다. 기존 내용 보호를 위해 작업을 중단합니다.")
        print("💡 (새 파일명으로 작성하거나 덮어쓰려면 -f / --force 옵션을 사용하세요.)")
        return
    
    # .py 파일과 .ipynb 파일 모두 찾기
    py_files = list(target_dir.glob("*.py"))
    ipynb_files = list(target_dir.glob("*.ipynb"))
    
    # 모든 파일을 합치고 정렬
    all_files = sorted(py_files + ipynb_files)
    
    # 실행 중인 스크립트 자기 자신(py 파일)은 목록에서 제외
    all_files = [f for f in all_files if f.resolve() != current_script_path]
    
    if not all_files:
        print(f"'{target_dir}' 디렉터리 내에 변환 대상 .py 또는 .ipynb 파일이 없습니다.")
        return

    md_lines = []
    md_lines.append(f"# {target_dir.name} 실습 코드 정리\n")

    for file_path in all_files:
        md_lines.append(f"## 파일: `{file_path.name}`\n")
        
        if file_path.suffix == '.ipynb':
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    notebook = json.load(f)
                except json.JSONDecodeError:
                    print(f"'{file_path.name}' 파일을 읽는 중 오류가 발생했습니다. (JSON 파싱 실패)")
                    continue
            
            for cell in notebook.get('cells', []):
                cell_type = cell.get('cell_type')
                source = cell.get('source', [])
                
                if not source:
                    continue
                    
                text = "".join(source)
                
                if cell_type == 'markdown':
                    md_lines.append(f"{text.strip()}\n")
                elif cell_type == 'code':
                    md_lines.append("```python\n" + text.strip() + "\n```\n")
                    md_lines.append("* [여기에 코드 설명을 작성하세요]\n")
                    md_lines.append("* [추가 설명]\n\n<br>\n")
                    
        elif file_path.suffix == '.py':
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
                
            md_lines.append("```python\n" + code_content.strip() + "\n```\n")
            md_lines.append("* [여기에 코드 설명을 작성하세요]\n")
            md_lines.append("* [추가 설명]\n\n<br>\n")
            
        md_lines.append("---\n")

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))
        
    print(f"통합 템플릿 생성 완료: {out_file.name} (저장 위치: {out_file.absolute()})")

def main():
    parser = argparse.ArgumentParser(description="디렉터리 내의 모든 .py와 .ipynb 파일을 '디렉터리_이름.md' 파일로 병합합니다.")
    parser.add_argument("directory", help="변환할 파일들이 있는 디렉터리 경로")
    parser.add_argument("-f", "--force", action="store_true", help="기존 .md 파일이 존재하더라도 강제로 덮어씁니다.")
    args = parser.parse_args()
    
    create_markdown_template(args.directory, overwrite=args.force)

if __name__ == '__main__':
    main()
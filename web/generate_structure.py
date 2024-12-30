import os

def generate_directory_tree(start_path, output_file, ignore_patterns=None):
    if ignore_patterns is None:
        ignore_patterns = [
            'node_modules', '.git', '__pycache__', 
            '.idea', '.vscode', 'dist', 'build/temp'
        ]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Project Directory Structure:\n")
        f.write("=========================\n\n")
        
        for root, dirs, files in os.walk(start_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in ignore_patterns)]
            
            level = root.replace(start_path, '').count(os.sep)
            indent = '  ' * level
            f.write(f'{indent}{os.path.basename(root)}/\n')
            
            sub_indent = '  ' * (level + 1)
            for file in sorted(files):
                if file.endswith(('.js', '.vue', '.ts', '.json', '.html', '.css')):
                    f.write(f'{sub_indent}{file}\n')

def main():
    # 假设脚本在项目根目录运行
    project_path = './web'  # 调整为你的项目路径
    output_file = 'project_structure.txt'
    
    if not os.path.exists(project_path):
        print(f"Error: Path {project_path} does not exist")
        return
    
    generate_directory_tree(project_path, output_file)
    print(f"Directory structure has been written to {output_file}")

if __name__ == "__main__":
    main()
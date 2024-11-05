import os
import markdown
import argparse

def analyze_directories(datasetpath):
    scene_stats = []
    
    for scene_name in os.listdir(datasetpath):
        scene_path = os.path.join(datasetpath, scene_name)
        
        if not os.path.isdir(scene_path):
            continue
        
        polycam_path = os.path.join(scene_path, "polycam")
        has_polycam = os.path.exists(polycam_path) and os.path.isdir(polycam_path)
        
        has_images = False
        has_correct_images = False
        
        if has_polycam:
            keyframes_path = os.path.join(polycam_path, "keyframes")
            if os.path.exists(keyframes_path) and os.path.isdir(keyframes_path):
                images_path = os.path.join(keyframes_path, "images")
                has_images = os.path.exists(images_path) and os.path.isdir(images_path)
                correct_images_path = os.path.join(keyframes_path, "corrected_images")
                has_correct_images = os.path.exists(correct_images_path) and os.path.isdir(correct_images_path)
        
        scene_stats.append({
            'name': scene_name,
            'has_polycam': has_polycam,
            'has_images': has_images,
            'has_correct_images': has_correct_images
        })
    
    return scene_stats

def generate_markdown_report(scene_stats):
    # Sort scenes: those with polycam scan first, then alphabetically
    sorted_stats = sorted(scene_stats, key=lambda x: (-x['has_polycam'], x['name']))
    
    md_content = "# Dataset Statistics\n\n"
    md_content += "| # | Scene Name | Polycam Data | Images | Corrected Images |\n"
    md_content += "|---|------------|--------------|--------|------------------|\n"
    
    for i, stat in enumerate(sorted_stats, 1):
        md_content += f"| {i} | {stat['name']} | {'✓' if stat['has_polycam'] else ''} | {'✓' if stat['has_images'] else ''} | {'✓' if stat['has_correct_images'] else ''} |\n"
    
    return md_content

def main():
    parser = argparse.ArgumentParser(description="Analyze dataset directory structure and generate statistics.")
    parser.add_argument("-d", "--dataset-dir", required=True, help="Path to the dataset directory")
    args = parser.parse_args()

    datasetpath = args.dataset_dir
    
    if not os.path.exists(datasetpath):
        print("The specified dataset directory does not exist.")
        return
    
    scene_stats = analyze_directories(datasetpath)
    md_report = generate_markdown_report(scene_stats)
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "dataset_statistics.md")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_report)
    
    print(f"\nStatistics report has been written to {output_file}")

if __name__ == "__main__":
    main()
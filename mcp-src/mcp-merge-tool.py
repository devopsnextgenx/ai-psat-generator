#!/usr/bin/env python3
"""
MCP (Merge Compare Patch) Tool
A utility for smartly comparing and merging text files locally.
"""

import argparse
import difflib
import sys
import os
from enum import Enum
import re
from typing import List, Tuple, Dict, Optional

class MergeStrategy(Enum):
    SMART = "smart"  # Use heuristics to determine best merge
    PREFER_LOCAL = "local"  # Prefer local file when conflicts occur
    PREFER_NEW = "new"  # Prefer new content when conflicts occur
    INTERACTIVE = "interactive"  # Prompt user for each conflict

class MergeBlock:
    def __init__(self, content, source, start_line=None, end_line=None):
        self.content = content
        self.source = source  # "local", "new", or "both"
        self.start_line = start_line
        self.end_line = end_line
    
    def __str__(self):
        return f"[{self.source}]: {self.content[:40]}{'...' if len(self.content) > 40 else ''}"

def read_file(file_path: str) -> str:
    """Read the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

def write_file(file_path: str, content: str) -> None:
    """Write content to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

def generate_diff(local_content: str, new_content: str) -> List[str]:
    """Generate a unified diff between local and new content."""
    local_lines = local_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    diff = difflib.unified_diff(
        local_lines, new_lines, 
        fromfile='local', tofile='new', 
        n=3  # Context lines
    )
    return list(diff)

def parse_hunk_header(hunk_header: str) -> Tuple[int, int, int, int]:
    """Parse a hunk header to get line numbers."""
    match = re.match(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', hunk_header)
    if not match:
        return 0, 0, 0, 0
    
    start1 = int(match.group(1))
    count1 = int(match.group(2) or 1)
    start2 = int(match.group(3))
    count2 = int(match.group(4) or 1)
    
    return start1, count1, start2, count2

def identify_semantic_blocks(content: str) -> List[dict]:
    """
    Identify semantic blocks in content (functions, classes, methods, etc.).
    Returns a list of dictionaries with start_line, end_line, type, and name.
    """
    blocks = []
    lines = content.splitlines()
    
    # Simple patterns for identifying code blocks
    patterns = {
        'function': r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*\)\s*:',
        'class': r'^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(.*\))?\s*:',
        'method': r'^\s+def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*\)\s*:',
        'comment_block': r'^\s*#.*',
        'docstring': r'^\s*"""',
        'imports': r'^\s*(?:import|from)\s+.*',
    }
    
    current_block = None
    indentation_stack = []
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Skip empty lines
        if not line.strip():
            continue
        
        # Calculate indentation level
        indentation = len(line) - len(line.lstrip())
        
        # Check if we're closing blocks due to dedentation
        while indentation_stack and indentation < indentation_stack[-1]:
            if current_block and 'end_line' not in current_block:
                current_block['end_line'] = line_num - 1
                blocks.append(current_block)
                current_block = None
            indentation_stack.pop()
        
        # Check for new block starts
        for block_type, pattern in patterns.items():
            match = re.match(pattern, line)
            if match:
                if block_type in ['function', 'class', 'method']:
                    if current_block and 'end_line' not in current_block:
                        current_block['end_line'] = line_num - 1
                        blocks.append(current_block)
                    
                    name = match.group(1) if match.groups() else None
                    current_block = {
                        'start_line': line_num,
                        'type': block_type,
                        'name': name
                    }
                    indentation_stack.append(indentation)
                    break
    
    # Close any remaining open blocks
    if current_block and 'end_line' not in current_block:
        current_block['end_line'] = len(lines)
        blocks.append(current_block)
    
    return blocks

def analyze_changes(diff_lines: List[str], local_content: str, new_content: str) -> List[MergeBlock]:
    """
    Analyze diff to create merge blocks with smart decisions.
    """
    local_lines = local_content.splitlines()
    new_lines = new_content.splitlines()
    
    # Identify semantic blocks
    local_blocks = identify_semantic_blocks(local_content)
    new_blocks = identify_semantic_blocks(new_content)
    
    merge_blocks = []
    current_hunk = None
    
    for line in diff_lines:
        if line.startswith('@@'):
            # New hunk
            current_hunk = line
            local_start, local_count, new_start, new_count = parse_hunk_header(line)
        elif line.startswith('-'):
            # Line removed (exists in local but not in new)
            content = line[1:]
            merge_blocks.append(MergeBlock(content, "local"))
        elif line.startswith('+'):
            # Line added (exists in new but not in local)
            content = line[1:]
            merge_blocks.append(MergeBlock(content, "new"))
        elif line.startswith(' '):
            # Context line (exists in both)
            content = line[1:]
            merge_blocks.append(MergeBlock(content, "both"))
    
    return merge_blocks

def apply_merge_strategy(merge_blocks: List[MergeBlock], strategy: MergeStrategy, local_content: str, new_content: str) -> str:
    """
    Apply the selected merge strategy to create the merged content.
    """
    merged_content = []
    
    if strategy == MergeStrategy.SMART:
        # Implement smart merge logic
        local_blocks = identify_semantic_blocks(local_content)
        new_blocks = identify_semantic_blocks(new_content)
        
        # Map of block names to their content (for both local and new)
        local_block_map = {block['name']: (block['start_line'], block['end_line']) 
                           for block in local_blocks if 'name' in block}
        new_block_map = {block['name']: (block['start_line'], block['end_line']) 
                         for block in new_blocks if 'name' in block}
        
        # Find blocks that exist in both
        common_blocks = set(local_block_map.keys()) & set(new_block_map.keys())
        local_only_blocks = set(local_block_map.keys()) - set(new_block_map.keys())
        new_only_blocks = set(new_block_map.keys()) - set(local_block_map.keys())
        
        # Build merged content by going through merge blocks
        for block in merge_blocks:
            if block.source == "both":
                merged_content.append(block.content)
            elif block.source == "local" and strategy == MergeStrategy.PREFER_LOCAL:
                merged_content.append(block.content)
            elif block.source == "new" and strategy == MergeStrategy.PREFER_NEW:
                merged_content.append(block.content)
            else:
                # For smart strategy, we need more context
                if block.source == "local":
                    # Check if this is part of a block that was completely replaced
                    # For now, default to keeping local version in ambiguous cases
                    merged_content.append(block.content)
                elif block.source == "new":
                    # Prefer new content for additions unless it conflicts with local
                    merged_content.append(block.content)
    
    elif strategy == MergeStrategy.PREFER_LOCAL:
        for block in merge_blocks:
            if block.source in ["local", "both"]:
                merged_content.append(block.content)
    
    elif strategy == MergeStrategy.PREFER_NEW:
        for block in merge_blocks:
            if block.source in ["new", "both"]:
                merged_content.append(block.content)
    
    elif strategy == MergeStrategy.INTERACTIVE:
        # Interactive merge
        i = 0
        while i < len(merge_blocks):
            block = merge_blocks[i]
            
            if block.source == "both":
                merged_content.append(block.content)
                i += 1
                continue
            
            # Found a conflict
            conflict_blocks = [block]
            j = i + 1
            while j < len(merge_blocks) and merge_blocks[j].source != "both":
                conflict_blocks.append(merge_blocks[j])
                j += 1
            
            # Display conflict
            print("\n====== CONFLICT ======")
            print("LOCAL:")
            for b in conflict_blocks:
                if b.source == "local":
                    print(f"  {b.content}")
            
            print("\nNEW:")
            for b in conflict_blocks:
                if b.source == "new":
                    print(f"  {b.content}")
            
            print("\nOptions:")
            print("1. Keep LOCAL version")
            print("2. Keep NEW version")
            print("3. Keep BOTH versions (local then new)")
            print("4. Edit manually")
            
            choice = input("Select option (1-4): ").strip()
            
            if choice == "1":
                for b in conflict_blocks:
                    if b.source == "local":
                        merged_content.append(b.content)
            elif choice == "2":
                for b in conflict_blocks:
                    if b.source == "new":
                        merged_content.append(b.content)
            elif choice == "3":
                for b in conflict_blocks:
                    if b.source in ["local", "new"]:
                        merged_content.append(b.content)
            elif choice == "4":
                print("Enter your edited version (type 'END' on a line by itself when finished):")
                edited_content = []
                while True:
                    line = input()
                    if line == "END":
                        break
                    edited_content.append(line)
                merged_content.extend(edited_content)
            
            i = j
    
    return "\n".join(merged_content)

def compare_files(local_path: str, new_content: str, strategy: MergeStrategy, output_path: Optional[str] = None) -> str:
    """
    Compare and merge two files based on the selected strategy.
    
    Args:
        local_path: Path to the local file
        new_content: Content string to compare with (from LLM or other source)
        strategy: Merge strategy to apply
        output_path: Optional path to write merged content
        
    Returns:
        Merged content as a string
    """
    local_content = read_file(local_path)
    
    # Generate diff
    diff_lines = generate_diff(local_content, new_content)
    
    # If there are no differences, return the local content
    if not diff_lines or len(diff_lines) <= 2:  # Just headers
        print("No differences found.")
        return local_content
    
    # Analyze changes to create merge blocks
    merge_blocks = analyze_changes(diff_lines, local_content, new_content)
    
    # Apply merge strategy
    merged_content = apply_merge_strategy(merge_blocks, strategy, local_content, new_content)
    
    # Write to output file if specified
    if output_path:
        write_file(output_path, merged_content)
        print(f"Merged content written to {output_path}")
    
    return merged_content

def main():
    parser = argparse.ArgumentParser(description="MCP: Merge Compare Patch Tool")
    parser.add_argument("local_file", help="Path to the local file")
    parser.add_argument(
        "--new-file", 
        help="Path to the new file for comparison (if not using --new-content)"
    )
    parser.add_argument(
        "--new-content", 
        help="String content to compare with (from LLM or other source)"
    )
    parser.add_argument(
        "--strategy", 
        choices=[s.value for s in MergeStrategy], 
        default=MergeStrategy.SMART.value,
        help="Merge strategy to apply"
    )
    parser.add_argument(
        "-o", "--output", 
        help="Path to write the merged content (defaults to stdout)"
    )
    parser.add_argument(
        "--diff-only", 
        action="store_true",
        help="Only show diff without merging"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.new_file and not args.new_content:
        parser.error("Either --new-file or --new-content must be provided")
    
    if args.new_file and args.new_content:
        parser.error("Cannot use both --new-file and --new-content simultaneously")
    
    # Get new content
    new_content = None
    if args.new_file:
        new_content = read_file(args.new_file)
    elif args.new_content:
        new_content = args.new_content
    
    # Generate diff if requested
    if args.diff_only:
        local_content = read_file(args.local_file)
        diff_lines = generate_diff(local_content, new_content)
        print("".join(diff_lines))
        return
    
    # Perform the merge
    strategy = MergeStrategy(args.strategy)
    merged_content = compare_files(args.local_file, new_content, strategy, args.output)
    
    # Print to stdout if no output file specified
    if not args.output:
        print(merged_content)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Orchid Genera Characteristic Clustering Analysis

This script analyzes vegetative characteristics of orchid genera from a markdown file
and creates clustering visualizations based on multiple distance measures:

1. Co-occurrence distance: How often characteristics appear together in the same genus
2. Jaccard similarity: Overlap of genera sharing each pair of characteristics
3. Semantic grouping: Domain-based hierarchical categorization

The output includes:
- Statistical summaries of characteristics and genera
- Similarity matrices for clustering
- Semantic hierarchical groupings
- Data for multiple visualization approaches
"""

import re
from collections import defaultdict
import json


def parse_genera_characteristics(md_file):
    """
    Parse the markdown file to extract characteristics for each genus.

    The function reads the markdown structure and identifies:
    - Genus sections (marked by '### Genus: ')
    - Characteristic categories (marked by '**Category:**')
    - Individual characteristic values (marked by '- ')

    Args:
        md_file (str): Path to the markdown file containing genera descriptions

    Returns:
        dict: Nested dictionary with structure:
              {genus_name: {
                  'characteristics': {category: [values]},
                  'raw_text': [all text lines]
              }}
    """
    with open(md_file, 'r') as f:
        content = f.read()

    genera = {}
    current_genus = None
    current_section = None

    # Regex patterns to identify structural elements
    # Pattern to match genus headings like "### Genus: Habenaria Willd."
    genus_pattern = r'### Genus: ([^\n]+)'

    # Pattern to match characteristic category headings like "**Growth Habit:**"
    section_pattern = r'\*\*([^*:]+):\*\*'

    lines = content.split('\n')

    for i, line in enumerate(lines):
        # Check if this line starts a new genus section
        genus_match = re.match(genus_pattern, line)
        if genus_match:
            current_genus = genus_match.group(1).strip()
            genera[current_genus] = {
                'characteristics': defaultdict(list),
                'raw_text': []
            }
            continue

        # Check if this line is a characteristic category heading
        if current_genus and line.strip().startswith('**') and ':**' in line:
            section_match = re.search(section_pattern, line)
            if section_match:
                current_section = section_match.group(1).strip()

        # Check if this line is a characteristic value (bullet point)
        if current_genus and line.strip().startswith('-'):
            # Store all text for potential future use
            genera[current_genus]['raw_text'].append(line.strip())

            # Associate this characteristic value with its category
            if current_section:
                genera[current_genus]['characteristics'][current_section].append(line.strip())

    return genera


def extract_all_characteristics(genera):
    """
    Extract all unique characteristic categories and map them to genera.

    This creates:
    1. A set of all unique characteristic types found across all genera
    2. A reverse mapping showing which genera possess each characteristic

    Args:
        genera (dict): Output from parse_genera_characteristics()

    Returns:
        tuple: (set of all characteristics,
                dict mapping each characteristic to set of genera that have it)
    """
    all_chars = set()
    char_to_genera = defaultdict(set)

    # Iterate through all genera and their characteristic categories
    for genus_name, data in genera.items():
        for char_type in data['characteristics'].keys():
            all_chars.add(char_type)
            char_to_genera[char_type].add(genus_name)

    return all_chars, char_to_genera


def calculate_cooccurrence(genera, all_chars):
    """
    Calculate co-occurrence matrix for characteristics.

    Distance Measure #1: Co-occurrence
    This measures how often pairs of characteristics appear together
    in the same genus. High co-occurrence suggests characteristics are
    functionally or taxonomically related.

    For example: "Pseudobulbs" and "Epiphytic" might co-occur frequently,
    suggesting a biological relationship between these features.

    Args:
        genera (dict): Parsed genera data
        all_chars (set): Set of all characteristic types

    Returns:
        tuple: (list of characteristic names in order,
                2D matrix where [i][j] = count of genera having both char i and char j)
    """
    char_list = sorted(list(all_chars))
    n = len(char_list)

    # Initialize n x n matrix with zeros
    # cooccurrence[i][j] will count how many genera have both characteristics i and j
    cooccurrence = [[0 for _ in range(n)] for _ in range(n)]

    # For each genus, find all pairs of characteristics it possesses
    for genus_name, data in genera.items():
        genus_chars = set(data['characteristics'].keys())
        # Get indices of all characteristics this genus has
        char_indices = [i for i, c in enumerate(char_list) if c in genus_chars]

        # Increment co-occurrence count for every pair
        # (including diagonal where i==j, showing how many genera have that characteristic)
        for i in char_indices:
            for j in char_indices:
                cooccurrence[i][j] += 1

    return char_list, cooccurrence


def jaccard_similarity(char1_genera, char2_genera):
    """
    Calculate Jaccard similarity coefficient between two characteristics.

    Distance Measure #2: Jaccard Similarity
    This measures the overlap in the set of genera that possess each characteristic.

    Jaccard = |A ∩ B| / |A ∪ B|

    Where:
    - A = set of genera with characteristic 1
    - B = set of genera with characteristic 2
    - |A ∩ B| = number of genera with both characteristics
    - |A ∪ B| = number of genera with either characteristic

    Example:
    - If "Rhizome" and "Roots" both appear in 5 genera,
      and there are 6 genera total with either or both,
      then Jaccard = 5/6 = 0.83 (very similar)

    Args:
        char1_genera (set): Set of genera possessing characteristic 1
        char2_genera (set): Set of genera possessing characteristic 2

    Returns:
        float: Similarity score from 0 (no overlap) to 1 (identical sets)
    """
    intersection = len(char1_genera & char2_genera)
    union = len(char1_genera | char2_genera)
    return intersection / union if union > 0 else 0


def create_semantic_clusters():
    """
    Create semantic/hierarchical clusters based on botanical domain knowledge.

    Distance Measure #3: Semantic Grouping
    This uses expert knowledge to group characteristics by their biological
    or morphological function. Unlike data-driven measures, this reflects
    how botanists conceptually organize plant features.

    Clusters represent major anatomical/functional divisions:
    - Underground Structures: Storage and anchoring organs
    - Stem Characteristics: Above-ground support structures
    - Leaf Attributes: Photosynthetic and descriptive features
    - Growth Form: Overall habit and size
    - Reproductive Structures: Flowers and fruits
    - Metadata: Taxonomic notes and references

    Returns:
        dict: Mapping from cluster name to list of characteristics in that cluster
    """
    return {
        'Underground Structures': [
            'Rhizome',
            'Roots',
            'Roots/Underground organs',
            'Pseudobulbs'
        ],
        'Stem Characteristics': [
            'Stem',
            'Stems'
        ],
        'Leaf Attributes': [
            'Leaves',
            'Arrangement',
            'Attachment',
            'Position',
            'Texture',
            'Shape',
            'Sheath',
            'Sheaths',
            'Size',
            'Dimensions',
            'Number',
            'Venation',
            'Surface',
            'Persistence'
        ],
        'Growth Form': [
            'Growth Habit',
            'Overall Plant Size'
        ],
        'Reproductive Structures': [
            'Inflorescence',
            'Capsule'
        ],
        'Metadata': [
            'Species noted',
            'Notes on species variation'
        ]
    }


def main():
    """
    Main analysis pipeline.

    Steps:
    1. Parse markdown file to extract genera and characteristics
    2. Build characteristic-to-genera mappings
    3. Calculate co-occurrence matrix (distance measure #1)
    4. Calculate Jaccard similarity for all characteristic pairs (distance measure #2)
    5. Create semantic clusters (distance measure #3)
    6. Compile statistics and output results to JSON

    Output file (characteristic_analysis.json) contains:
    - Statistics: counts and distributions
    - Characteristics list: all unique characteristic types
    - Char to genera mapping: which genera have which characteristics
    - Semantic clusters: domain-based groupings
    - Jaccard similarities: pairwise similarity scores
    - Co-occurrence matrix: how often characteristics appear together
    """
    # Step 1: Parse the markdown file
    genera = parse_genera_characteristics('/workspace/mcleish.genera.md')

    # Step 2: Extract all characteristics and build reverse mapping
    all_chars, char_to_genera = extract_all_characteristics(genera)

    # Step 3: Calculate co-occurrence matrix
    char_list, cooccurrence = calculate_cooccurrence(genera, all_chars)

    # Calculate basic statistics
    stats = {
        'total_genera': len(genera),
        'total_characteristics': len(all_chars),
        'characteristics_per_genus': {g: len(d['characteristics']) for g, d in genera.items()},
        'genera_per_characteristic': {c: len(char_to_genera[c]) for c in all_chars}
    }

    # Step 4: Calculate Jaccard similarities for all characteristic pairs
    # Only store similarities above threshold (0.3) to reduce noise
    jaccard_matrix = {}
    for c1 in all_chars:
        jaccard_matrix[c1] = {}
        for c2 in all_chars:
            if c1 != c2:
                sim = jaccard_similarity(char_to_genera[c1], char_to_genera[c2])
                if sim > 0.3:  # Only keep significant similarities (>30% overlap)
                    jaccard_matrix[c1][c2] = sim

    # Step 5: Create semantic clusters based on botanical knowledge
    semantic_clusters = create_semantic_clusters()

    # Step 6: Compile all results into output structure
    output = {
        'statistics': stats,
        'characteristics_list': sorted(list(all_chars)),
        'char_to_genera': {c: sorted(list(g)) for c, g in char_to_genera.items()},
        'semantic_clusters': semantic_clusters,
        'jaccard_similarities': jaccard_matrix,
        'cooccurrence': {
            'characteristics': char_list,
            'matrix': cooccurrence
        }
    }

    # Write results to JSON file for use by visualization tools
    with open('/workspace/characteristic_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary to console
    print("Analysis complete. Results saved to characteristic_analysis.json")
    print(f"\nTotal genera: {stats['total_genera']}")
    print(f"Total characteristics: {stats['total_characteristics']}")
    print(f"\nCharacteristics per genus:")
    for g, count in sorted(stats['characteristics_per_genus'].items()):
        print(f"  {g}: {count}")
    print(f"\nGenera per characteristic:")
    for c, count in sorted(stats['genera_per_characteristic'].items()):
        print(f"  {c}: {count}")


if __name__ == '__main__':
    main()

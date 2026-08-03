# Orchid Genera Characteristic Clustering Analysis Tools

This directory contains scripts for analyzing and visualizing vegetative characteristics of orchid genera.

## Scripts

### 1. `analyze_characteristics.js`
**Purpose**: Extract and analyze characteristics from the markdown documentation

**What it does**:
- Parses the `mcleish.genera.md` file to extract all genera and their characteristics
- Computes three distance/similarity measures:
  1. **Co-occurrence matrix**: Counts how often characteristic pairs appear together
  2. **Jaccard similarity**: Measures overlap in genera possessing each characteristic pair
  3. **Semantic clustering**: Groups characteristics by botanical function
- Outputs analysis to `characteristic_analysis.json`

**Usage**:
```bash
node bin/analyze_characteristics.js
```

**Output**: `/workspace/characteristic_analysis.json` containing:
- Statistics (counts, distributions)
- Characteristic-to-genera mappings
- Similarity matrices
- Semantic clusters

### 2. `visualize_clusters.js`
**Purpose**: Generate multiple visualization formats from the analysis data

**What it does**:
- Reads `characteristic_analysis.json`
- Generates four visualization types:
  - **A. Semantic Hierarchy**: Tree showing functional groupings
  - **B. Network Graph**: Characteristics connected by similarity
  - **C. Bipartite Graph**: Genera-to-characteristic relationships
  - **D. Presence/Absence Matrix**: Tabular heatmap view
- Outputs to `clustering_section.md` and appends to main document

**Usage**:
```bash
node bin/visualize_clusters.js
```

**Output**: `/workspace/clustering_section.md` with Mermaid diagrams and tables

## Distance Measures Explained

### 1. Co-occurrence Distance
**Concept**: Characteristics that appear together frequently are functionally related.

**Example**: If "Rhizome" and "Roots" both appear in 5 of 8 genera together, they have high co-occurrence (5).

**Use case**: Identifies characteristics that are developmentally or evolutionarily linked.

### 2. Jaccard Similarity
**Formula**: J(A,B) = |A ∩ B| / |A ∪ B|

**Concept**: Measures the overlap of genera sets for two characteristics.

**Example**:
- Characteristic A appears in genera {1, 2, 3, 4}
- Characteristic B appears in genera {2, 3, 4, 5}
- Intersection: {2, 3, 4} = 3 genera
- Union: {1, 2, 3, 4, 5} = 5 genera
- Jaccard = 3/5 = 0.6 (60% similarity)

**Use case**: Identifies characteristics that co-vary across taxonomic groups. High Jaccard suggests characteristics are diagnostic for similar groups of genera.

### 3. Semantic Grouping
**Concept**: Expert-defined functional categories based on botanical knowledge.

**Categories**:
- **Underground Structures**: Rhizomes, roots, tubers, pseudobulbs
- **Stem Characteristics**: Stem type, orientation, texture
- **Leaf Attributes**: Shape, texture, arrangement, venation, etc.
- **Growth Form**: Overall habit and size
- **Reproductive Structures**: Inflorescence, fruits
- **Metadata**: Taxonomic notes and species lists

**Use case**: Organizes characteristics the way botanists think about them, useful for systematic descriptions and identification keys.

## Visualization Approaches

### A. Semantic Hierarchy (Tree/Dendrogram)
**Best for**: Understanding functional organization
**Format**: Mermaid tree diagram
**Interpretation**: Shows how characteristics are conceptually grouped by botanical function
**When to use**: Teaching, creating structured keys, organizing descriptions

### B. Network Graph
**Best for**: Discovering unexpected relationships
**Format**: Mermaid network with weighted edges
**Interpretation**:
- Nodes = characteristics
- Edges = Jaccard similarity > 0.5
- Clusters = characteristics that co-occur frequently
**When to use**: Exploratory analysis, finding diagnostic character combinations

### C. Bipartite Graph
**Best for**: Comparative taxonomy
**Format**: Mermaid graph with two node types
**Interpretation**:
- Left nodes = Genera
- Right nodes = Characteristics
- Edges = possession
- Visual patterns show which genera share features
**When to use**: Genus comparison, identification, finding unique characteristics

### D. Presence/Absence Matrix
**Best for**: Quick reference and identification
**Format**: ASCII table with symbols (●/○)
**Interpretation**:
- Rows = Genera
- Columns = Characteristics
- Quick visual scanning to find distinguishing features
**When to use**: Field identification, creating dichotomous keys, spotting patterns

## Suggested Additional Visualizations

### 1. Interactive Network (D3.js or Cytoscape)
- Allow zooming and filtering by similarity threshold
- Color nodes by semantic cluster
- Click to highlight genera possessing that characteristic

### 2. Phylogenetic-style Tree
- Use hierarchical clustering on the co-occurrence matrix
- Create dendrogram showing characteristic relationships
- Could reveal deeper biological patterns

### 3. Heatmap with Clustering
- Reorder rows/columns by similarity
- Use color intensity for co-occurrence strength
- Reveals blocks of related characteristics

### 4. Chord Diagram
- Shows flow between genera and characteristics
- Particularly good for highlighting key characteristics
- Visually striking for presentations

## Data Files

- **Input**: `/workspace/mcleish.genera.md` - Source documentation
- **Output**: `/workspace/characteristic_analysis.json` - Computed metrics
- **Output**: `/workspace/clustering_section.md` - Visualization section
- **Final**: `/workspace/mcleish.genera.md` - Updated with clustering section

## Dependencies

- Node.js (for JavaScript execution)
- Mermaid-compatible markdown renderer (for viewing diagrams)

## Future Enhancements

1. **Statistical Testing**: Add p-values for characteristic associations
2. **Phylogenetic Integration**: Incorporate known phylogenetic relationships
3. **Interactive Dashboard**: Web-based exploration tool
4. **Machine Learning**: Predictive models for genus identification
5. **Image Integration**: Link to herbarium specimens or photos
6. **Geographic Patterns**: Map characteristics to biogeographic regions

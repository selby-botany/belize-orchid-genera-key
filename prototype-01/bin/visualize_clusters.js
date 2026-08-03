#!/usr/bin/env node
/**
 * Orchid Genera Characteristic Visualization Generator
 *
 * This script generates multiple visualization formats from the characteristic
 * clustering analysis:
 *
 * 1. Mermaid diagrams (for markdown rendering)
 *    - Network graph showing characteristic relationships
 *    - Hierarchical semantic clusters
 *    - Genera-to-characteristic bipartite graph
 *
 * 2. DOT/Graphviz format (for high-quality static images)
 *
 * 3. ASCII art dendrograms (for simple text viewing)
 *
 * Suggested visualization approaches:
 * A. Network graph with characteristics as nodes, edges weighted by Jaccard similarity
 * B. Hierarchical tree showing semantic clusters
 * C. Bipartite graph: genera on left, characteristics on right, edges show possession
 * D. Heatmap-style table showing characteristic presence/absence by genus
 */

const fs = require('fs');

/**
 * Load the analysis data from JSON file.
 *
 * @returns {Object} Parsed analysis data
 */
function loadAnalysisData() {
    const data = fs.readFileSync('/workspace/characteristic_analysis.json', 'utf8');
    return JSON.parse(data);
}

/**
 * Generate a Mermaid network graph showing characteristic relationships.
 *
 * Visualization A: Network Graph
 * - Nodes = characteristics
 * - Edges = Jaccard similarity > threshold
 * - Edge thickness proportional to similarity
 * - Node color by semantic cluster
 *
 * This shows which characteristics tend to co-occur across genera,
 * revealing functional or evolutionary relationships.
 *
 * @param {Object} data - Analysis data
 * @returns {string} Mermaid diagram code
 */
function generateMermaidNetwork(data) {
    const { jaccard_similarities, semantic_clusters } = data;

    // Create color mapping for clusters
    const charToCluster = {};
    const clusterColors = {
        'Underground Structures': '#8B4513',
        'Stem Characteristics': '#228B22',
        'Leaf Attributes': '#32CD32',
        'Growth Form': '#4169E1',
        'Reproductive Structures': '#FF1493',
        'Metadata': '#808080'
    };

    for (const [cluster, chars] of Object.entries(semantic_clusters)) {
        for (const char of chars) {
            charToCluster[char] = cluster;
        }
    }

    let mermaid = 'graph TD\n';

    // Add nodes with cluster-based styling
    const nodeIds = {};
    let nodeCounter = 0;

    for (const char of data.characteristics_list) {
        const nodeId = `N${nodeCounter++}`;
        nodeIds[char] = nodeId;
        const cluster = charToCluster[char] || 'Unknown';
        mermaid += `  ${nodeId}["${char}"]\n`;
    }

    // Add edges for significant similarities
    const edges = [];
    for (const [c1, similarities] of Object.entries(jaccard_similarities)) {
        for (const [c2, sim] of Object.entries(similarities)) {
            if (sim > 0.5 && nodeIds[c1] && nodeIds[c2]) {
                // Only show strong relationships
                edges.push({ from: c1, to: c2, weight: sim });
            }
        }
    }

    // Deduplicate edges (since similarity is symmetric)
    const seenEdges = new Set();
    for (const edge of edges) {
        const edgeKey = [edge.from, edge.to].sort().join('|');
        if (!seenEdges.has(edgeKey)) {
            seenEdges.add(edgeKey);
            const thickness = Math.round(edge.weight * 5);
            mermaid += `  ${nodeIds[edge.from]} --- ${nodeIds[edge.to]}\n`;
        }
    }

    return mermaid;
}

/**
 * Generate a Mermaid hierarchical diagram showing semantic clusters.
 *
 * Visualization B: Semantic Hierarchy
 * - Root = "Orchid Characteristics"
 * - Level 1 = Semantic clusters (functional groups)
 * - Level 2 = Individual characteristics
 *
 * This shows the expert-defined taxonomic organization of characteristics,
 * useful for understanding how botanists think about plant features.
 *
 * @param {Object} data - Analysis data
 * @returns {string} Mermaid diagram code
 */
function generateMermaidHierarchy(data) {
    const { semantic_clusters } = data;

    let mermaid = 'graph TD\n';
    mermaid += '  Root["Orchid Vegetative Characteristics"]\n';

    let clusterCounter = 0;
    for (const [cluster, chars] of Object.entries(semantic_clusters)) {
        const clusterId = `C${clusterCounter++}`;
        mermaid += `  Root --> ${clusterId}["${cluster}"]\n`;

        let charCounter = 0;
        for (const char of chars) {
            const charId = `${clusterId}_${charCounter++}`;
            mermaid += `  ${clusterId} --> ${charId}["${char}"]\n`;
        }
    }

    return mermaid;
}

/**
 * Generate a Mermaid bipartite graph connecting genera to characteristics.
 *
 * Visualization C: Genera-Characteristic Bipartite Graph
 * - Left nodes = Genera (8 nodes)
 * - Right nodes = Characteristics (13 nodes)
 * - Edges = Genus possesses that characteristic
 *
 * This directly shows the data structure: which genera have which features.
 * Useful for comparative analysis and identification keys.
 *
 * @param {Object} data - Analysis data
 * @returns {string} Mermaid diagram code
 */
function generateMermaidBipartite(data) {
    const { char_to_genera, statistics } = data;

    let mermaid = 'graph LR\n';

    // Create genus nodes
    const genera = Object.keys(statistics.characteristics_per_genus);
    const genusNodes = {};
    for (let i = 0; i < genera.length; i++) {
        const genusId = `G${i}`;
        genusNodes[genera[i]] = genusId;
        // Shorten genus names for readability
        const shortName = genera[i].split(' ')[0];
        mermaid += `  ${genusId}["${shortName}"]\n`;
    }

    // Create characteristic nodes
    const charNodes = {};
    let charCounter = 0;
    for (const char of data.characteristics_list) {
        const charId = `C${charCounter++}`;
        charNodes[char] = charId;
        mermaid += `  ${charId}["${char}"]\n`;
    }

    // Create edges
    for (const [char, genuslist] of Object.entries(char_to_genera)) {
        for (const genus of genuslist) {
            if (genusNodes[genus] && charNodes[char]) {
                mermaid += `  ${genusNodes[genus]} --> ${charNodes[char]}\n`;
            }
        }
    }

    return mermaid;
}

/**
 * Generate an ASCII table/heatmap showing characteristic presence.
 *
 * Visualization D: Presence/Absence Matrix
 * Rows = Genera
 * Columns = Characteristics
 * Cell = ● (present) or ○ (absent)
 *
 * This compact representation allows quick visual scanning to identify
 * which characteristics distinguish genera.
 *
 * @param {Object} data - Analysis data
 * @returns {string} ASCII table
 */
function generatePresenceMatrix(data) {
    const { char_to_genera, statistics } = data;

    const genera = Object.keys(statistics.characteristics_per_genus).sort();
    const chars = data.characteristics_list;

    // Create reverse mapping: genus -> set of characteristics
    const genusToChars = {};
    for (const genus of genera) {
        genusToChars[genus] = new Set();
    }
    for (const [char, genuslist] of Object.entries(char_to_genera)) {
        for (const genus of genuslist) {
            if (genusToChars[genus]) {
                genusToChars[genus].add(char);
            }
        }
    }

    // Build table
    let table = '| Genus | ' + chars.map(c => c.substring(0, 10)).join(' | ') + ' |\n';
    table += '|' + '-'.repeat(15) + '|' + chars.map(() => '-'.repeat(12)).join('|') + '|\n';

    for (const genus of genera) {
        const shortGenus = genus.split(' ')[0];
        let row = `| ${shortGenus.padEnd(13)} |`;
        for (const char of chars) {
            const marker = genusToChars[genus].has(char) ? '●' : '○';
            row += ` ${marker.padEnd(10)} |`;
        }
        table += row + '\n';
    }

    return table;
}

/**
 * Generate summary statistics for the clustering section.
 *
 * @param {Object} data - Analysis data
 * @returns {string} Markdown-formatted statistics
 */
function generateStatistics(data) {
    const { statistics, jaccard_similarities } = data;

    let stats = '## Clustering Statistics\n\n';
    stats += `- **Total Genera**: ${statistics.total_genera}\n`;
    stats += `- **Total Characteristics**: ${statistics.total_characteristics}\n`;
    stats += `- **Average characteristics per genus**: ${(Object.values(statistics.characteristics_per_genus).reduce((a, b) => a + b, 0) / statistics.total_genera).toFixed(1)}\n`;

    // Find most and least common characteristics
    const sorted = Object.entries(statistics.genera_per_characteristic).sort((a, b) => b[1] - a[1]);
    stats += `- **Most common characteristic**: ${sorted[0][0]} (${sorted[0][1]} genera)\n`;
    stats += `- **Least common characteristics**: ${sorted.slice(-3).map(([c, n]) => `${c} (${n})`).join(', ')}\n\n`;

    // Find strongest similarities
    const allSims = [];
    for (const [c1, sims] of Object.entries(jaccard_similarities)) {
        for (const [c2, sim] of Object.entries(sims)) {
            if (c1 < c2) {  // Avoid duplicates
                allSims.push({ c1, c2, sim });
            }
        }
    }
    allSims.sort((a, b) => b.sim - a.sim);

    stats += '### Strongest Characteristic Relationships (Jaccard Similarity)\n\n';
    for (const { c1, c2, sim } of allSims.slice(0, 5)) {
        stats += `- **${c1}** ↔ **${c2}**: ${(sim * 100).toFixed(1)}% overlap\n`;
    }

    return stats;
}

/**
 * Main function to generate all visualizations.
 */
function main() {
    console.log('Loading analysis data...');
    const data = loadAnalysisData();

    console.log('Generating visualizations...');

    // Generate all visualizations
    const networkGraph = generateMermaidNetwork(data);
    const hierarchyGraph = generateMermaidHierarchy(data);
    const bipartiteGraph = generateMermaidBipartite(data);
    const presenceMatrix = generatePresenceMatrix(data);
    const statistics = generateStatistics(data);

    // Compile into a markdown section
    let output = '# Characteristic Clustering Analysis\n\n';
    output += statistics + '\n\n';

    output += '## Distance Measures\n\n';
    output += 'Three distance/similarity measures were used:\n\n';
    output += '1. **Co-occurrence**: How often characteristic pairs appear in the same genus\n';
    output += '2. **Jaccard Similarity**: Overlap in the set of genera possessing each characteristic\n';
    output += '   - Formula: J(A,B) = |A ∩ B| / |A ∪ B|\n';
    output += '   - Range: 0 (no overlap) to 1 (identical)\n';
    output += '3. **Semantic Grouping**: Expert-defined functional/anatomical categories\n\n';

    output += '## Visualization A: Semantic Hierarchy\n\n';
    output += 'This shows characteristics organized by botanical function:\n\n';
    output += '```mermaid\n' + hierarchyGraph + '```\n\n';

    output += '## Visualization B: Characteristic Network\n\n';
    output += 'Characteristics connected by Jaccard similarity > 0.5:\n\n';
    output += '```mermaid\n' + networkGraph + '```\n\n';

    output += '## Visualization C: Genera-Characteristic Relationships\n\n';
    output += 'Bipartite graph showing which genera possess which characteristics:\n\n';
    output += '```mermaid\n' + bipartiteGraph + '```\n\n';

    output += '## Visualization D: Presence/Absence Matrix\n\n';
    output += 'Quick reference table (● = present, ○ = absent):\n\n';
    output += presenceMatrix + '\n\n';

    // Save to file
    fs.writeFileSync('/workspace/clustering_section.md', output);

    console.log('Visualizations generated and saved to clustering_section.md');
    console.log('\nSummary:');
    console.log('- Network graph: Shows characteristic co-occurrence patterns');
    console.log('- Hierarchical tree: Shows semantic organization');
    console.log('- Bipartite graph: Shows genera-characteristic mappings');
    console.log('- Matrix table: Shows presence/absence patterns');
}

if (require.main === module) {
    main();
}

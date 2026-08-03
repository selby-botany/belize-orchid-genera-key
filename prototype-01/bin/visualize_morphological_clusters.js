#!/usr/bin/env node
/**
 * Morphological Feature Visualization Generator
 *
 * Creates visualizations at the correct granularity: specific morphological descriptions.
 */

const fs = require('fs');

function loadData() {
    return JSON.parse(fs.readFileSync('/workspace/morphological_analysis.json', 'utf8'));
}

/**
 * Generate statistics section with meaningful metrics.
 */
function generateStatistics(data) {
    const { statistics, features, clusters, ontology } = data;

    let output = '# Morphological Feature Clustering Analysis\n\n';
    output += '## Overview\n\n';
    output += 'This analysis operates at the **morphological feature level**, examining specific\n';
    output += 'descriptive characteristics rather than broad categories.\n\n';

    output += '## Statistics\n\n';
    output += `- **Total Genera**: ${statistics.total_genera}\n`;
    output += `- **Total Unique Morphological Features**: ${statistics.total_unique_features}\n`;
    output += `- **Total Unique Morphological Terms**: ${statistics.total_unique_terms}\n`;
    output += `- **Similarity Clusters Found**: ${clusters.length}\n`;
    output += `- **Average features per genus**: ${(Object.values(statistics.features_per_genus).reduce((a,b) => a+b, 0) / statistics.total_genera).toFixed(1)}\n\n`;

    output += '### Features per Genus\n\n';
    const sorted = Object.entries(statistics.features_per_genus).sort((a,b) => b[1] - a[1]);
    for (const [genus, count] of sorted) {
        output += `- **${genus}**: ${count} features\n`;
    }
    output += '\n';

    return output;
}

/**
 * Generate table showing example feature similarities.
 */
function generateSimilarityExamples(data) {
    const { similarities } = data;

    let output = '## Example Feature Similarities\n\n';
    output += 'Morphological features with high semantic similarity (based on shared descriptive terms):\n\n';
    output += '| Similarity | Feature 1 | Feature 2 |\n';
    output += '|------------|-----------|------------|\n';

    const examples = [];
    for (const [f1, others] of Object.entries(similarities)) {
        for (const [f2, sim] of Object.entries(others)) {
            if (sim >= 0.5 && f1 < f2) {  // Avoid duplicates
                examples.push({ f1, f2, sim });
            }
        }
    }

    examples.sort((a, b) => b.sim - a.sim);

    for (const ex of examples.slice(0, 20)) {
        const f1Short = ex.f1.length > 60 ? ex.f1.substring(0, 57) + '...' : ex.f1;
        const f2Short = ex.f2.length > 60 ? ex.f2.substring(0, 57) + '...' : ex.f2;
        output += `| ${(ex.sim * 100).toFixed(0)}% | ${f1Short} | ${f2Short} |\n`;
    }

    output += '\n';
    return output;
}

/**
 * Generate morphological term ontology visualization.
 */
function generateOntology(data) {
    const { ontology } = data;

    let output = '## Morphological Term Ontology\n\n';
    output += 'Terms organized by the morphological context in which they appear:\n\n';

    const contexts = Object.entries(ontology.contextTerms).sort();

    for (const [context, terms] of contexts) {
        if (terms.length > 0) {
            output += `### ${context}\n\n`;
            output += `**Terms**: ${terms.join(', ')}\n\n`;
        }
    }

    return output;
}

/**
 * Generate feature clusters showing semantically similar descriptions.
 */
function generateFeatureClusters(data) {
    const { clusters, features } = data;

    let output = '## Morphological Feature Clusters\n\n';
    output += 'Groups of features with high semantic similarity (sharing morphological terms):\n\n';

    const largeClusters = clusters.filter(c => c.size >= 3).slice(0, 15);

    for (let i = 0; i < largeClusters.length; i++) {
        const cluster = largeClusters[i];
        output += `### Cluster ${i + 1}: ${cluster.size} related features\n\n`;

        for (const feat of cluster.features) {
            const featureData = features[feat];
            if (featureData) {
                const genera = featureData.genera.join(', ');
                output += `- **${feat}**\n`;
                output += `  - Genera: ${genera}\n`;
            }
        }
        output += '\n';
    }

    return output;
}

/**
 * Generate network visualization showing similar morphological features.
 */
function generateMermaidNetwork(data) {
    const { similarities, features } = data;

    let output = '## Visualization: Feature Similarity Network\n\n';
    output += 'This network shows morphological features (nodes) connected by semantic similarity (edges).\n';
    output += 'Only features with >60% term overlap are shown.\n\n';

    output += '```mermaid\ngraph TD\n';

    // Find features with strong similarities
    const nodeMap = new Map();
    const edges = [];
    let nodeCounter = 0;

    for (const [f1, others] of Object.entries(similarities)) {
        for (const [f2, sim] of Object.entries(others)) {
            if (sim >= 0.6 && f1 < f2) {
                if (!nodeMap.has(f1)) {
                    nodeMap.set(f1, `N${nodeCounter++}`);
                }
                if (!nodeMap.has(f2)) {
                    nodeMap.set(f2, `N${nodeCounter++}`);
                }
                edges.push({ f1, f2, sim });
            }
        }
    }

    // Limit to most connected nodes
    if (nodeMap.size > 30) {
        const nodeDegree = new Map();
        for (const { f1, f2 } of edges) {
            nodeDegree.set(f1, (nodeDegree.get(f1) || 0) + 1);
            nodeDegree.set(f2, (nodeDegree.get(f2) || 0) + 1);
        }

        const topNodes = Array.from(nodeDegree.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 30)
            .map(([node]) => node);

        const topNodeSet = new Set(topNodes);
        nodeMap.clear();
        nodeCounter = 0;
        for (const node of topNodes) {
            nodeMap.set(node, `N${nodeCounter++}`);
        }

        edges.length = 0;
        for (const [f1, others] of Object.entries(similarities)) {
            for (const [f2, sim] of Object.entries(others)) {
                if (sim >= 0.6 && f1 < f2 && topNodeSet.has(f1) && topNodeSet.has(f2)) {
                    edges.push({ f1, f2, sim });
                }
            }
        }
    }

    // Add nodes with shortened labels
    for (const [feature, nodeId] of nodeMap.entries()) {
        const featureData = features[feature];
        let label = feature;

        // Shorten label for readability
        if (featureData && featureData.subcategory) {
            label = `${featureData.subcategory}: ${featureData.description.substring(0, 20)}`;
        } else if (feature.length > 30) {
            label = feature.substring(0, 27) + '...';
        }

        output += `  ${nodeId}["${label}"]\n`;
    }

    // Add edges
    for (const { f1, f2 } of edges) {
        const n1 = nodeMap.get(f1);
        const n2 = nodeMap.get(f2);
        if (n1 && n2) {
            output += `  ${n1} --- ${n2}\n`;
        }
    }

    output += '```\n\n';
    return output;
}

/**
 * Generate comparison table by feature category.
 */
function generateFeatureComparisonTable(data) {
    const { features, statistics } = data;

    let output = '## Feature Comparison by Category\n\n';

    // Group features by category and subcategory
    const byCategory = {};

    for (const [featDesc, featData] of Object.entries(features)) {
        const cat = featData.category;
        const subcat = featData.subcategory || 'General';

        if (!byCategory[cat]) {
            byCategory[cat] = {};
        }
        if (!byCategory[cat][subcat]) {
            byCategory[cat][subcat] = [];
        }

        byCategory[cat][subcat].push({
            description: featData.description,
            genera: featData.genera
        });
    }

    // Generate tables for interesting categories
    const interestingCategories = ['Leaves', 'Roots', 'Rhizome', 'Stems', 'Growth Habit'];

    for (const category of interestingCategories) {
        if (!byCategory[category]) continue;

        output += `### ${category}\n\n`;

        for (const [subcategory, feats] of Object.entries(byCategory[category])) {
            if (feats.length > 1) {  // Only show if there's variation
                output += `#### ${subcategory}\n\n`;
                output += '| Description | Genera |\n';
                output += '|-------------|--------|\n';

                for (const feat of feats) {
                    const genera = feat.genera.map(g => g.split(' ')[0]).join(', ');
                    output += `| ${feat.description} | ${genera} |\n`;
                }
                output += '\n';
            }
        }
    }

    return output;
}

/**
 * Main function.
 */
function main() {
    console.log('Loading morphological analysis data...');
    const data = loadData();

    console.log('Generating visualizations...');

    let output = '';
    output += generateStatistics(data);
    output += '\n---\n\n';
    output += generateSimilarityExamples(data);
    output += '\n---\n\n';
    output += generateFeatureClusters(data);
    output += '\n---\n\n';
    output += generateMermaidNetwork(data);
    output += '\n---\n\n';
    output += generateFeatureComparisonTable(data);
    output += '\n---\n\n';
    output += generateOntology(data);

    fs.writeFileSync('/workspace/morphological_clustering.md', output);

    console.log('Morphological clustering analysis complete!');
    console.log('Output saved to: morphological_clustering.md');
}

if (require.main === module) {
    main();
}

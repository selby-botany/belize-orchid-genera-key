#!/usr/bin/env node
/**
 * Orchid Genera Characteristic Clustering Analysis
 *
 * This script analyzes vegetative characteristics of orchid genera from a markdown file
 * and creates clustering visualizations based on multiple distance measures:
 *
 * 1. Co-occurrence distance: How often characteristics appear together in the same genus
 * 2. Jaccard similarity: Overlap of genera sharing each pair of characteristics
 * 3. Semantic grouping: Domain-based hierarchical categorization
 *
 * The output includes:
 * - Statistical summaries of characteristics and genera
 * - Similarity matrices for clustering
 * - Semantic hierarchical groupings
 * - Data for multiple visualization approaches
 */

const fs = require('fs');
const path = require('path');

/**
 * Parse the markdown file to extract characteristics for each genus.
 *
 * The function reads the markdown structure and identifies:
 * - Genus sections (marked by '### Genus: ')
 * - Characteristic categories (marked by '**Category:**')
 * - Individual characteristic values (marked by '- ')
 *
 * @param {string} mdFile - Path to the markdown file containing genera descriptions
 * @returns {Object} Nested object with structure:
 *                   {genus_name: {
 *                       characteristics: {category: [values]},
 *                       raw_text: [all text lines]
 *                   }}
 */
function parseGeneraCharacteristics(mdFile) {
    const content = fs.readFileSync(mdFile, 'utf8');
    const genera = {};
    let currentGenus = null;
    let currentSection = null;

    // Regex patterns to identify structural elements
    // Pattern to match genus headings like "### Genus: Habenaria Willd."
    const genusPattern = /^### Genus: ([^\n]+)$/;

    // Pattern to match characteristic category headings like "**Growth Habit:**"
    const sectionPattern = /\*\*([^*:]+):\*\*/;

    const lines = content.split('\n');

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // Check if this line starts a new genus section
        const genusMatch = line.match(genusPattern);
        if (genusMatch) {
            currentGenus = genusMatch[1].trim();
            genera[currentGenus] = {
                characteristics: {},
                raw_text: []
            };
            continue;
        }

        // Check if this line is a characteristic category heading
        if (currentGenus && line.trim().startsWith('**') && line.includes(':**')) {
            const sectionMatch = line.match(sectionPattern);
            if (sectionMatch) {
                currentSection = sectionMatch[1].trim();
                if (!genera[currentGenus].characteristics[currentSection]) {
                    genera[currentGenus].characteristics[currentSection] = [];
                }
            }
        }

        // Check if this line is a characteristic value (bullet point)
        if (currentGenus && line.trim().startsWith('-')) {
            // Store all text for potential future use
            genera[currentGenus].raw_text.push(line.trim());

            // Associate this characteristic value with its category
            if (currentSection) {
                genera[currentGenus].characteristics[currentSection].push(line.trim());
            }
        }
    }

    return genera;
}

/**
 * Extract all unique characteristic categories and map them to genera.
 *
 * This creates:
 * 1. A set of all unique characteristic types found across all genera
 * 2. A reverse mapping showing which genera possess each characteristic
 *
 * @param {Object} genera - Output from parseGeneraCharacteristics()
 * @returns {Object} {allChars: Set, charToGenera: Object}
 */
function extractAllCharacteristics(genera) {
    const allChars = new Set();
    const charToGenera = {};

    // Iterate through all genera and their characteristic categories
    for (const [genusName, data] of Object.entries(genera)) {
        for (const charType of Object.keys(data.characteristics)) {
            allChars.add(charType);
            if (!charToGenera[charType]) {
                charToGenera[charType] = new Set();
            }
            charToGenera[charType].add(genusName);
        }
    }

    return { allChars, charToGenera };
}

/**
 * Calculate co-occurrence matrix for characteristics.
 *
 * Distance Measure #1: Co-occurrence
 * This measures how often pairs of characteristics appear together
 * in the same genus. High co-occurrence suggests characteristics are
 * functionally or taxonomically related.
 *
 * For example: "Pseudobulbs" and "Epiphytic" might co-occur frequently,
 * suggesting a biological relationship between these features.
 *
 * @param {Object} genera - Parsed genera data
 * @param {Set} allChars - Set of all characteristic types
 * @returns {Object} {characteristics: Array, matrix: 2D Array}
 *                   where matrix[i][j] = count of genera having both char i and char j
 */
function calculateCooccurrence(genera, allChars) {
    const charList = Array.from(allChars).sort();
    const n = charList.length;

    // Initialize n x n matrix with zeros
    // cooccurrence[i][j] will count how many genera have both characteristics i and j
    const cooccurrence = Array(n).fill(0).map(() => Array(n).fill(0));

    // For each genus, find all pairs of characteristics it possesses
    for (const [genusName, data] of Object.entries(genera)) {
        const genusChars = new Set(Object.keys(data.characteristics));
        // Get indices of all characteristics this genus has
        const charIndices = charList
            .map((c, i) => genusChars.has(c) ? i : -1)
            .filter(i => i >= 0);

        // Increment co-occurrence count for every pair
        // (including diagonal where i==j, showing how many genera have that characteristic)
        for (const i of charIndices) {
            for (const j of charIndices) {
                cooccurrence[i][j]++;
            }
        }
    }

    return { characteristics: charList, matrix: cooccurrence };
}

/**
 * Calculate Jaccard similarity coefficient between two characteristics.
 *
 * Distance Measure #2: Jaccard Similarity
 * This measures the overlap in the set of genera that possess each characteristic.
 *
 * Jaccard = |A ∩ B| / |A ∪ B|
 *
 * Where:
 * - A = set of genera with characteristic 1
 * - B = set of genera with characteristic 2
 * - |A ∩ B| = number of genera with both characteristics
 * - |A ∪ B| = number of genera with either characteristic
 *
 * Example:
 * - If "Rhizome" and "Roots" both appear in 5 genera,
 *   and there are 6 genera total with either or both,
 *   then Jaccard = 5/6 = 0.83 (very similar)
 *
 * @param {Set} char1Genera - Set of genera possessing characteristic 1
 * @param {Set} char2Genera - Set of genera possessing characteristic 2
 * @returns {number} Similarity score from 0 (no overlap) to 1 (identical sets)
 */
function jaccardSimilarity(char1Genera, char2Genera) {
    const intersection = new Set([...char1Genera].filter(x => char2Genera.has(x)));
    const union = new Set([...char1Genera, ...char2Genera]);
    return union.size > 0 ? intersection.size / union.size : 0;
}

/**
 * Create semantic/hierarchical clusters based on botanical domain knowledge.
 *
 * Distance Measure #3: Semantic Grouping
 * This uses expert knowledge to group characteristics by their biological
 * or morphological function. Unlike data-driven measures, this reflects
 * how botanists conceptually organize plant features.
 *
 * Clusters represent major anatomical/functional divisions:
 * - Underground Structures: Storage and anchoring organs
 * - Stem Characteristics: Above-ground support structures
 * - Leaf Attributes: Photosynthetic and descriptive features
 * - Growth Form: Overall habit and size
 * - Reproductive Structures: Flowers and fruits
 * - Metadata: Taxonomic notes and references
 *
 * @returns {Object} Mapping from cluster name to list of characteristics in that cluster
 */
function createSemanticClusters() {
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
    };
}

/**
 * Main analysis pipeline.
 *
 * Steps:
 * 1. Parse markdown file to extract genera and characteristics
 * 2. Build characteristic-to-genera mappings
 * 3. Calculate co-occurrence matrix (distance measure #1)
 * 4. Calculate Jaccard similarity for all characteristic pairs (distance measure #2)
 * 5. Create semantic clusters (distance measure #3)
 * 6. Compile statistics and output results to JSON
 *
 * Output file (characteristic_analysis.json) contains:
 * - Statistics: counts and distributions
 * - Characteristics list: all unique characteristic types
 * - Char to genera mapping: which genera have which characteristics
 * - Semantic clusters: domain-based groupings
 * - Jaccard similarities: pairwise similarity scores
 * - Co-occurrence matrix: how often characteristics appear together
 */
function main() {
    // Step 1: Parse the markdown file
    const genera = parseGeneraCharacteristics('/workspace/mcleish.genera.md');

    // Step 2: Extract all characteristics and build reverse mapping
    const { allChars, charToGenera } = extractAllCharacteristics(genera);

    // Step 3: Calculate co-occurrence matrix
    const cooccurrence = calculateCooccurrence(genera, allChars);

    // Calculate basic statistics
    const stats = {
        total_genera: Object.keys(genera).length,
        total_characteristics: allChars.size,
        characteristics_per_genus: {},
        genera_per_characteristic: {}
    };

    for (const [g, data] of Object.entries(genera)) {
        stats.characteristics_per_genus[g] = Object.keys(data.characteristics).length;
    }

    for (const [c, genusSet] of Object.entries(charToGenera)) {
        stats.genera_per_characteristic[c] = genusSet.size;
    }

    // Step 4: Calculate Jaccard similarities for all characteristic pairs
    // Only store similarities above threshold (0.3) to reduce noise
    const jaccardMatrix = {};
    const charArray = Array.from(allChars);

    for (const c1 of charArray) {
        jaccardMatrix[c1] = {};
        for (const c2 of charArray) {
            if (c1 !== c2) {
                const sim = jaccardSimilarity(charToGenera[c1], charToGenera[c2]);
                if (sim > 0.3) {  // Only keep significant similarities (>30% overlap)
                    jaccardMatrix[c1][c2] = sim;
                }
            }
        }
    }

    // Step 5: Create semantic clusters based on botanical knowledge
    const semanticClusters = createSemanticClusters();

    // Convert Sets to Arrays for JSON serialization
    const charToGeneraObj = {};
    for (const [char, genusSet] of Object.entries(charToGenera)) {
        charToGeneraObj[char] = Array.from(genusSet).sort();
    }

    // Step 6: Compile all results into output structure
    const output = {
        statistics: stats,
        characteristics_list: Array.from(allChars).sort(),
        char_to_genera: charToGeneraObj,
        semantic_clusters: semanticClusters,
        jaccard_similarities: jaccardMatrix,
        cooccurrence: cooccurrence
    };

    // Write results to JSON file for use by visualization tools
    fs.writeFileSync(
        '/workspace/characteristic_analysis.json',
        JSON.stringify(output, null, 2)
    );

    // Print summary to console
    console.log('Analysis complete. Results saved to characteristic_analysis.json');
    console.log(`\nTotal genera: ${stats.total_genera}`);
    console.log(`Total characteristics: ${stats.total_characteristics}`);
    console.log('\nCharacteristics per genus:');
    for (const [g, count] of Object.entries(stats.characteristics_per_genus).sort()) {
        console.log(`  ${g}: ${count}`);
    }
    console.log('\nGenera per characteristic:');
    for (const [c, count] of Object.entries(stats.genera_per_characteristic).sort()) {
        console.log(`  ${c}: ${count}`);
    }
}

if (require.main === module) {
    main();
}

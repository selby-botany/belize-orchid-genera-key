#!/usr/bin/env node
/**
 * Orchid Morphological Feature Analysis - Detailed Level
 *
 * This script analyzes at the correct granularity: the specific morphological
 * descriptions within each characteristic category.
 *
 * For example, instead of "Leaves" (present in all genera), we extract:
 * - "Leaves > Texture > thin, membranous"
 * - "Leaves > Texture > flat, plicate, thin"
 * - "Leaves > Shape > ovate to lanceolate"
 *
 * Distance measures focus on semantic similarity of morphological terms:
 * 1. Term overlap (Jaccard on tokenized descriptions)
 * 2. Morphological term ontology-based distance
 * 3. Edit distance for similar phrases
 */

const fs = require('fs');

/**
 * Parse morphological features at the detailed sub-characteristic level.
 *
 * Instead of tracking "Leaves" as a single characteristic, this extracts:
 * - Category: "Leaves"
 * - Sub-category: "Texture"
 * - Description: "thin, membranous to somewhat fleshy"
 *
 * @param {string} mdFile - Path to markdown file
 * @returns {Object} Detailed feature extraction
 */
function parseMorphologicalFeatures(mdFile) {
    const content = fs.readFileSync(mdFile, 'utf8');
    const genera = {};
    let currentGenus = null;
    let currentCategory = null;

    const genusPattern = /^### Genus: ([^\n]+)$/;
    const categoryPattern = /^\*\*([^*:]+):\*\*$/;
    const subFeaturePattern = /^- \*\*([^*:]+):\*\* (.+)$/;
    const simpleFeaturePattern = /^- (.+)$/;

    const lines = content.split('\n');

    for (let line of lines) {
        // Check for new genus
        const genusMatch = line.match(genusPattern);
        if (genusMatch) {
            currentGenus = genusMatch[1].trim();
            genera[currentGenus] = {
                features: []  // Array of {category, subcategory, description, fullPath}
            };
            currentCategory = null;
            continue;
        }

        if (!currentGenus) continue;

        // Check for category heading (e.g., "**Leaves:**")
        const categoryMatch = line.match(categoryPattern);
        if (categoryMatch) {
            currentCategory = categoryMatch[1].trim();
            continue;
        }

        // Check for sub-feature with explicit property (e.g., "- **Texture:** thin, membranous")
        const subFeatureMatch = line.match(subFeaturePattern);
        if (subFeatureMatch && currentCategory) {
            const subcategory = subFeatureMatch[1].trim();
            const description = subFeatureMatch[2].trim();
            genera[currentGenus].features.push({
                category: currentCategory,
                subcategory: subcategory,
                description: description,
                fullPath: `${currentCategory} > ${subcategory}`,
                fullDescription: `${currentCategory} > ${subcategory} > ${description}`
            });
            continue;
        }

        // Check for simple feature (e.g., "- Terrestrial plants")
        const simpleFeatureMatch = line.match(simpleFeaturePattern);
        if (simpleFeatureMatch && currentCategory) {
            const description = simpleFeatureMatch[1].trim();
            genera[currentGenus].features.push({
                category: currentCategory,
                subcategory: null,
                description: description,
                fullPath: currentCategory,
                fullDescription: `${currentCategory} > ${description}`
            });
        }
    }

    return genera;
}

/**
 * Tokenize a morphological description into terms.
 *
 * Extracts meaningful morphological descriptors while removing noise words.
 *
 * Example:
 * "thin, membranous to somewhat fleshy" → ["thin", "membranous", "fleshy"]
 *
 * @param {string} text - Morphological description
 * @returns {Set} Set of normalized terms
 */
function tokenizeMorphologicalTerms(text) {
    // Normalize text
    text = text.toLowerCase();

    // Remove parenthetical explanations
    text = text.replace(/\([^)]*\)/g, ' ');

    // Split on common separators
    const tokens = text.split(/[,;\/]|\s+or\s+|\s+and\s+/);

    // Clean and filter tokens
    const terms = new Set();
    const stopwords = new Set(['to', 'the', 'a', 'an', 'of', 'with', 'in', 'on', 'at', 'by', 'for']);

    for (let token of tokens) {
        // Clean token
        token = token.trim().replace(/^[-–—]\s*/, '').replace(/[.:;,]$/, '');

        // Split multi-word phrases and extract key terms
        const words = token.split(/\s+/).filter(w => w.length > 2 && !stopwords.has(w));

        for (const word of words) {
            if (word.length > 0) {
                terms.add(word);
            }
        }
    }

    return terms;
}

/**
 * Calculate Jaccard similarity based on morphological term overlap.
 *
 * This measures semantic similarity by comparing the actual descriptive terms.
 *
 * Example:
 * - "thin, membranous to fleshy" → {thin, membranous, fleshy}
 * - "membranous to somewhat fleshy" → {membranous, somewhat, fleshy}
 * - Intersection: {membranous, fleshy} = 2
 * - Union: {thin, membranous, fleshy, somewhat} = 4
 * - Jaccard = 2/4 = 0.5
 *
 * @param {string} desc1 - First description
 * @param {string} desc2 - Second description
 * @returns {number} Similarity score 0-1
 */
function calculateTermSimilarity(desc1, desc2) {
    const terms1 = tokenizeMorphologicalTerms(desc1);
    const terms2 = tokenizeMorphologicalTerms(desc2);

    const intersection = new Set([...terms1].filter(t => terms2.has(t)));
    const union = new Set([...terms1, ...terms2]);

    return union.size > 0 ? intersection.size / union.size : 0;
}

/**
 * Build a morphological term ontology from the dataset.
 *
 * This identifies related terms that often co-occur or are used in similar contexts.
 * For example: "ovate", "elliptic", "lanceolate" are all leaf shapes.
 *
 * @param {Object} genera - Parsed genera data
 * @returns {Object} Term relationships and categories
 */
function buildMorphologicalOntology(genera) {
    const termsByContext = {};  // Maps context (e.g., "Leaves > Shape") to set of terms
    const termCooccurrence = {}; // Tracks which terms appear together

    // Collect all terms by their context
    for (const [genusName, data] of Object.entries(genera)) {
        for (const feature of data.features) {
            const context = feature.fullPath;

            if (!termsByContext[context]) {
                termsByContext[context] = new Set();
            }

            // Extract terms from this description
            const terms = tokenizeMorphologicalTerms(feature.description);
            for (const term of terms) {
                termsByContext[context].add(term);

                // Track co-occurrence
                if (!termCooccurrence[term]) {
                    termCooccurrence[term] = new Set();
                }
                for (const otherTerm of terms) {
                    if (term !== otherTerm) {
                        termCooccurrence[term].add(otherTerm);
                    }
                }
            }
        }
    }

    // Convert to regular objects for JSON serialization
    const ontology = {
        contextTerms: {},
        cooccurrence: {}
    };

    for (const [context, terms] of Object.entries(termsByContext)) {
        ontology.contextTerms[context] = Array.from(terms).sort();
    }

    for (const [term, coterms] of Object.entries(termCooccurrence)) {
        ontology.cooccurrence[term] = Array.from(coterms).sort();
    }

    return ontology;
}

/**
 * Extract all unique morphological features across genera.
 *
 * Returns features at the proper granularity (category > subcategory > description).
 *
 * @param {Object} genera - Parsed genera data
 * @returns {Object} All unique features and their genera mappings
 */
function extractAllFeatures(genera) {
    const allFeatures = new Map();  // fullDescription -> {genera: Set, feature: Object}

    for (const [genusName, data] of Object.entries(genera)) {
        for (const feature of data.features) {
            const key = feature.fullDescription;

            if (!allFeatures.has(key)) {
                allFeatures.set(key, {
                    genera: new Set(),
                    feature: feature
                });
            }

            allFeatures.get(key).genera.add(genusName);
        }
    }

    return allFeatures;
}

/**
 * Calculate pairwise similarities between all morphological features.
 *
 * Uses term-based Jaccard similarity to measure semantic distance.
 *
 * @param {Map} allFeatures - All unique features
 * @returns {Object} Similarity matrix
 */
function calculateFeatureSimilarities(allFeatures) {
    const features = Array.from(allFeatures.keys());
    const similarities = {};

    for (let i = 0; i < features.length; i++) {
        const feat1 = features[i];
        const desc1 = allFeatures.get(feat1).feature.description;

        similarities[feat1] = {};

        for (let j = i + 1; j < features.length; j++) {
            const feat2 = features[j];
            const desc2 = allFeatures.get(feat2).feature.description;

            // Only compare features from the same category
            const cat1 = allFeatures.get(feat1).feature.category;
            const cat2 = allFeatures.get(feat2).feature.category;

            if (cat1 === cat2) {
                const similarity = calculateTermSimilarity(desc1, desc2);
                if (similarity > 0.1) {  // Only store if some similarity
                    similarities[feat1][feat2] = similarity;
                    if (!similarities[feat2]) {
                        similarities[feat2] = {};
                    }
                    similarities[feat2][feat1] = similarity;
                }
            }
        }
    }

    return similarities;
}

/**
 * Group features by semantic similarity using simple threshold clustering.
 *
 * @param {Map} allFeatures - All unique features
 * @param {Object} similarities - Pairwise similarities
 * @param {number} threshold - Similarity threshold for clustering
 * @returns {Array} Array of clusters
 */
function clusterBySimilarity(allFeatures, similarities, threshold = 0.3) {
    const features = Array.from(allFeatures.keys());
    const visited = new Set();
    const clusters = [];

    for (const feature of features) {
        if (visited.has(feature)) continue;

        const cluster = [feature];
        visited.add(feature);

        // Find all similar features
        for (const other of features) {
            if (visited.has(other)) continue;

            if (similarities[feature] && similarities[feature][other] >= threshold) {
                cluster.push(other);
                visited.add(other);
            }
        }

        if (cluster.length > 0) {
            clusters.push({
                features: cluster,
                size: cluster.length,
                representative: cluster[0]
            });
        }
    }

    return clusters.sort((a, b) => b.size - a.size);
}

/**
 * Main analysis pipeline.
 */
function main() {
    console.log('Parsing morphological features at detailed level...');
    const genera = parseMorphologicalFeatures('/workspace/mcleish.genera.md');

    console.log('Building morphological term ontology...');
    const ontology = buildMorphologicalOntology(genera);

    console.log('Extracting all unique features...');
    const allFeatures = extractAllFeatures(genera);

    console.log('Calculating feature similarities...');
    const similarities = calculateFeatureSimilarities(allFeatures);

    console.log('Clustering similar features...');
    const clusters = clusterBySimilarity(allFeatures, similarities);

    // Calculate statistics
    const stats = {
        total_genera: Object.keys(genera).length,
        total_unique_features: allFeatures.size,
        features_per_genus: {},
        unique_terms: new Set()
    };

    for (const [genusName, data] of Object.entries(genera)) {
        stats.features_per_genus[genusName] = data.features.length;

        for (const feature of data.features) {
            const terms = tokenizeMorphologicalTerms(feature.description);
            for (const term of terms) {
                stats.unique_terms.add(term);
            }
        }
    }

    stats.total_unique_terms = stats.unique_terms.size;
    delete stats.unique_terms;  // Don't serialize the Set

    // Convert Map to object for JSON serialization
    const featuresObj = {};
    for (const [key, value] of allFeatures.entries()) {
        featuresObj[key] = {
            genera: Array.from(value.genera),
            category: value.feature.category,
            subcategory: value.feature.subcategory,
            description: value.feature.description,
            fullPath: value.feature.fullPath
        };
    }

    // Compile output
    const output = {
        statistics: stats,
        genera: genera,
        features: featuresObj,
        ontology: ontology,
        similarities: similarities,
        clusters: clusters
    };

    fs.writeFileSync('/workspace/morphological_analysis.json', JSON.stringify(output, null, 2));

    console.log('\nAnalysis complete!');
    console.log(`Total genera: ${stats.total_genera}`);
    console.log(`Total unique morphological features: ${allFeatures.size}`);
    console.log(`Total unique morphological terms: ${stats.total_unique_terms}`);
    console.log(`Similarity clusters found: ${clusters.length}`);
    console.log(`\nTop 5 largest feature clusters:`);
    for (let i = 0; i < Math.min(5, clusters.length); i++) {
        console.log(`  Cluster ${i + 1}: ${clusters[i].size} similar features`);
        console.log(`    Representative: ${clusters[i].representative}`);
    }
}

if (require.main === module) {
    main();
}

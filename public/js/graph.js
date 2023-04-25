let neoViz;

function draw() {
    const config = {
        containerId: "viz",
        neo4j: {
            serverUrl: "bolt://localhost:7687",
            serverUser: "neo4j",
            serverPassword: "securepass123",
        },
        visConfig: {
            nodes: {
                borderWidth: 2,
                borderWidthSelected: 5,
            },
            physics: {
                barnesHut: {
                    gravitationalConstant: -7000,
                    springLength: 300,
                },
                minVelocity: 0.75
            }
        },
        interaction: { hover: true },
        labels: {
            Book: {
                label: "title",
                [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                    function: {
                        title: NeoVis.objectToTitleHtml,
                    },
                    static: {
                        color: "#002B5B",
                    },
                }
            },
            Tag: {
                label: "name",
                // color: "green",
                [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                    static: {
                        color: "#E4DCCF",
                    },
                }
            }

        },
        // initialCypher: "MATCH (t:Tag)<-[r:HAS_TAG]-(b:Book) RETURN t,b,r"
        initialCypher: "MATCH p=()-[r:HAS_TAG]->() RETURN p"
    };

    viz = new NeoVis.default(config);
    viz.render();
}
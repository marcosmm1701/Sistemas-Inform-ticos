MATCH p = shortestPath((reiner:Director {name: "Reiner, Carl"})-[*]-(smyth:Actor {name: "Smyth, Lisa (I)"}))
RETURN p AS ShortestPath, length(p) AS PathLength;


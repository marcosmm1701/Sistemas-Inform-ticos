MATCH (actor1:Actor)-[:ACTED_IN]->(:Movie)<-[:ACTED_IN]-(common:Actor),
      (common)-[:ACTED_IN]->(:Movie)<-[:ACTED_IN]-(actor2:Actor)
WHERE actor1.name <> "Winston, Hattie"
  AND actor2.name = "Winston, Hattie"
  AND NOT (actor1)-[:ACTED_IN]->(:Movie)<-[:ACTED_IN]-(actor2)
RETURN DISTINCT actor1.name AS ActorName
ORDER BY actor1.name
LIMIT 10;

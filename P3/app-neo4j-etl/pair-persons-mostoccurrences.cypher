MATCH (person1:Person)-[:ACTED_IN|DIRECTED]->(movie:Movie)<-[:ACTED_IN|DIRECTED]-(person2:Person)
WHERE person1.personid <> person2.personid
WITH person1, person2, COUNT(movie) AS collaborations
WHERE collaborations > 1
RETURN person1.name AS Person1, person2.name AS Person2, collaborations
ORDER BY collaborations DESC;

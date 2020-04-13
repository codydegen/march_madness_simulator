--Identify all the fan groups and sort by descending average points
SELECT groups.name, count(entries.id) AS entries, 
       avg(entries.espn_score) AS average 
FROM entries
LEFT JOIN group_entries ON entries.id = group_entries.entry_id
LEFT JOIN groups ON group_entries.group_id = groups.id
GROUP BY groups.name 
HAVING entries > 10 AND groups.name LIKE "%Fans of%" 
ORDER BY average DESC;

--Identify all entries which have data scraped for them
SELECT * FROM entries WHERE name <> 'NULL'

-- Identify most common predicted winner scores, Loser scores, and margin of victory
SELECT predicted_score_winner, COUNT(name) FROM entries 
WHERE name <> 'NULL' AND predicted_score_winner <> 0  
GROUP BY 1 ORDER BY 2 DESC

SELECT predicted_score_loser, COUNT(name) FROM entries 
WHERE name <> 'NULL' AND predicted_score_winner <> 0  
GROUP BY 1 ORDER BY 2 DESC

SELECT predicted_score_winner-predicted_score_loser AS margin_of_victory, COUNT(name)   
FROM entries 
WHERE name <> 'NULL' AND predicted_score_winner <> 0  
GROUP BY 1 ORDER BY 2 DESC

-- Grab Random entries from database
SELECT * FROM entries 
WHERE id IN 
    (SELECT id FROM entries 
     WHERE name <> 'NULL' 
     ORDER BY RANDOM() 
     LIMIT 1000)


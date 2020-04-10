--Identify all the fan groups and sort by descending average points
SELECT groups.name, count(entries.id) as entries, avg(entries.espn_score) As average FROM entries
LEFT JOIN group_entries ON entries.id = group_entries.entry_id
LEFT JOIN groups ON group_entries.group_id = groups.id
GROUP BY groups.name 
HAVING entries > 10 AND groups.name LIKE "%Fans of%" 
ORDER BY average DESC;


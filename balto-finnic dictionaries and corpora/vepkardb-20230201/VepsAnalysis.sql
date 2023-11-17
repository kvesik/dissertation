USE vepkar;
show tables;
select DISTINCT affix
FROM lemma_wordform
JOIN (SELECT * FROM lemmas WHERE lang_id=1) AS veps_lemmas 
ON veps_lemmas.id=lemma_wordform.lemma_id
ORDER BY affix;

SELECT DISTINCT wordforms.id AS wf_id, wordforms.wordform, wordforms.wordform_for_search, 
veps_lemmas.id as lemma_id, veps_lemmas.lemma, veps_lemmas.lemma_for_search, 
lemma_wordform.affix
FROM wordforms
JOIN lemma_wordform
ON wordforms.id=lemma_wordform.wordform_id
JOIN (SELECT * FROM lemmas WHERE lang_id=1) AS veps_lemmas
ON veps_lemmas.id=lemma_wordform.lemma_id
WHERE (wordform RLIKE '^[^aouõäüöie]*[äüö][^aouõäüöie]+[äüö]'
OR wordform RLIKE '^[^aouõäüöie]*[aouõ][^aouõäüöie]+[aouõ]')
AND wordform NOT LIKE '% %';




USE vepkar;
SELECT DISTINCT wordforms.id AS wf_id, wordforms.wordform, wordforms.wordform_for_search, 
veps_lemmas.id as lemma_id, veps_lemmas.lemma, veps_lemmas.lemma_for_search, 
lemma_wordform.affix
FROM wordforms
JOIN lemma_wordform
ON wordforms.id=lemma_wordform.wordform_id
JOIN (SELECT * FROM lemmas WHERE lang_id=1) AS veps_lemmas
ON veps_lemmas.id=lemma_wordform.lemma_id
WHERE wordform NOT LIKE '% %';

SELECT DISTINCT wordforms.id AS wf_id, wordforms.wordform, wordforms.wordform_for_search, 
veps_lemmas.id as lemma_id, veps_lemmas.lemma, veps_lemmas.lemma_for_search, 
lemma_wordform.affix
FROM wordforms
JOIN lemma_wordform
ON wordforms.id=lemma_wordform.wordform_id
JOIN (SELECT * FROM lemmas WHERE lang_id=1) AS veps_lemmas
ON veps_lemmas.id=lemma_wordform.lemma_id
WHERE (wordform LIKE '%a%'
	OR wordform LIKE '%u%'
	OR wordform LIKE '%o%'
    	OR wordform LIKE '%õ%')
    AND (wordform LIKE '%ä%'
	OR wordform LIKE '%ü%'
	OR wordform LIKE '%ö%')
    AND (wordform NOT LIKE '% %');



select DISTINCT affix
FROM lemma_wordform
WHERE affix RLIKE '^gi';
    
WHERE (wordform LIKE '%a%'
	OR wordform LIKE '%u%'
	OR wordform LIKE '%o%'
    OR wordform LIKE '%õ%')
    AND (wordform LIKE '%ä%'
	OR wordform LIKE '%ü%'
	OR wordform LIKE '%ö%');

SELECT DISTINCT wordforms.wordform, veps_lemmas.lemma, lemma_wordform.affix
FROM wordforms
JOIN lemma_wordform
ON wordforms.id=lemma_wordform.wordform_id
JOIN (SELECT * FROM lemmas WHERE lang_id=1) AS veps_lemmas
ON veps_lemmas.id=lemma_wordform.lemma_id
WHERE (wordform RLIKE '^[^aouõAOUÕäüöÜÖÄieIE]*[äüöÜÖÄ]')
AND (wordform RLIKE '[äüöÜÖÄ][^aouõAOUÕäüöÜÖÄieIE]+')
AND (wordform RLIKE '([^aouõAOUÕäüöÜÖÄieIE]+[ieIE]+)+')
AND (wordform NOT LIKE '% %');

SELECT 'clömillesdo' RLIKE '^[^aouõAOUÕäüöÜÖÄieIE]*[äüöÜÖÄ][^aouõAOUÕäüöÜÖÄieIE]*[ieIE]*';
SELECT 'clömillesdo' RLIKE 'cl[äüöÜÖÄ]';
SHOW VARIABLES;

^[^aouõAOUÕäüöÜÖÄieIE]*[äüöÜÖÄ]([^aouõAOUÕäüöÜÖÄieIE]+[ieIE]+)+[^aouõAOUÕäüöÜÖÄieIE]+[aouõAOUÕ]

SELECT DISTINCT wordforms.wordform, veps_lemmas.lemma, lemma_wordform.affix
FROM wordforms
JOIN lemma_wordform
ON wordforms.id=lemma_wordform.wordform_id
JOIN (SELECT * FROM lemmas WHERE lang_id=1) AS veps_lemmas
ON veps_lemmas.id=lemma_wordform.lemma_id
WHERE (wordform RLIKE '[äüöÜÖÄ]' AND wordform RLIKE '[aouõAOUÕ]')
AND wordform NOT LIKE '% %';  



WHERE (wordform RLIKE '^[^aouõäüöie]*[aouõ]([^aouõäüöie]+[ie]+)+[^aouõäüöie]+[aouõ]'
OR wordform RLIKE '^[^aouõäüöie]*[äüö]([^aouõäüöie]+[ie]+)+[^aouõäüöie]+[äüö]')

OR wordform RLIKE '^[^aouõäüöie]*[aouõ][^aouõäüöie]+[aouõ]'
OR wordform RLIKE '^[^aouõäüöie]*[aouõ][^aouõäüöie]+[äüö]')
äüö

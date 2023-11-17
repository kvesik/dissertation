show databases;
USE vepkar2;
SELECT 'clömäillesdo' RLIKE '^[^aouõAOUÕäüöÜÖÄieIE]*[äüöÜÖÄ][^aouõAOUÕäüöÜÖÄieIE]+[äüöÜÖÄ][^aouõAOUÕäüöÜÖÄieIE]+'
	OR RLIKE '^[^aouõAOUÕäüöÜÖÄieIE]*[äüöÜÖÄ][^aouõAOUÕäüöÜÖÄieIE]+[äüöÜÖÄ][^aouõAOUÕäüöÜÖÄieIE]+'
SELECT 'clömäillesdo' RLIKE 'ä[ieIE]?';

WITH fourcols AS (
        SELECT DISTINCT wordforms.wordform, veps_lemmas.lemma, lemma_wordform.affix, SUBSTRING(wordforms.wordform, 1, CHAR_LENGTH(wordforms.wordform) - CHAR_LENGTH(affix)) AS stem
        FROM wordforms
        JOIN lemma_wordform
        ON wordforms.id=lemma_wordform.wordform_id
        JOIN (SELECT * FROM lemmas WHERE lang_id=1) AS veps_lemmas
        ON veps_lemmas.id=lemma_wordform.lemma_id
        WHERE wordform NOT LIKE '% %'
        AND (wordform NOT RLIKE '[aouõAOUÕäüöÜÖÄieIE][aouõAOUÕäüöÜÖÄieIE][aouõAOUÕäüöÜÖÄieIE]')
        AND (wordform NOT RLIKE '[äüöÜÖÄ][aouAOU]')
		AND (wordform NOT RLIKE '[aouAOU][äüöÜÖÄ]')
		AND (wordform LIKE CONCAT('%', affix))
)
SELECT DISTINCT * FROM fourcols
WHERE (stem RLIKE '[aouAOUäüöÜÖÄieIE]+[^aouAOUäüöÜÖÄieIE]+[aouAOUäüöÜÖÄieIE]+')
AND (stem RLIKE '^([^aouAOUäüöÜÖÄieIE]|[ieIE])*[aouAOUäüöÜÖÄieIE]+([^aouAOUäüöÜÖÄieIE]|[ieIE])*$');
OR (stem RLIKE '[aouAOU].*[^aouAOUäüöÜÖÄieIE]+.*[äüöÜÖÄ]'));

SELECT DISTINCT wordforms.wordform, veps_lemmas.lemma, lemma_wordform.affix
FROM wordforms
JOIN lemma_wordform
ON wordforms.id=lemma_wordform.wordform_id
JOIN (SELECT * FROM lemmas WHERE lang_id=1) AS veps_lemmas
ON veps_lemmas.id=lemma_wordform.lemma_id
WHERE wordform NOT LIKE '% %'
AND (wordform NOT RLIKE '[aouõAOUÕäüöÜÖÄieIE][aouõAOUÕäüöÜÖÄieIE][aouõAOUÕäüöÜÖÄieIE]')
AND (wordform NOT RLIKE '[äüöÜÖÄ][aouAOU]')
AND (wordform NOT RLIKE '[aouAOU][äüöÜÖÄ]')
AND (CHAR_LENGTH(affix) > 0)
AND (wordform NOT RLIKE CONCAT(affix, '$'));
-- Igal dim_time real peab täpselt üks päevaosa lipp olema tõene.
-- Päevaosad (is_morning, is_afternoon, is_evening, is_night) peavad katma kogu ööpäeva
-- ega tohi omavahel kattuda. Booleanid teisendatakse arvuks ja summa peab olema täpselt 1.
-- Test läbib, kui päring tagastab 0 rida.

SELECT
    full_time,
    is_morning,
    is_afternoon,
    is_evening,
    is_night
FROM {{ ref('dim_time') }}
WHERE (is_morning::int + is_afternoon::int + is_evening::int + is_night::int) <> 1

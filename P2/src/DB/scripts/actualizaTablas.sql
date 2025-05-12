-- 1. Crea tabla temporal para los países asociados a cada película
CREATE TABLE imdb_moviecountries_temp (
    country_id SERIAL PRIMARY KEY,
    movieid INTEGER NOT NULL,
    country CHARACTER VARYING(32) NOT NULL,
    FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON DELETE CASCADE
);

-- Inserta los datos existentes en la nueva tabla temporal
INSERT INTO imdb_moviecountries_temp (movieid, country)
SELECT movieid, country FROM imdb_moviecountries;

-- Elimina la tabla antigua
DROP TABLE IF EXISTS imdb_moviecountries;

-- Renombra la tabla temporal para que tenga el nombre de la tabla original
ALTER TABLE imdb_moviecountries_temp RENAME TO imdb_moviecountries;


-- 2. Crea tabla temporal para los géneros asociados a cada película
CREATE TABLE imdb_moviegenres_temp (
    genre_id SERIAL PRIMARY KEY,
    movieid INTEGER NOT NULL,
    genre CHARACTER VARYING(32) NOT NULL,
    FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON DELETE CASCADE
);

-- Inserta los datos existentes en la nueva tabla temporal
INSERT INTO imdb_moviegenres_temp (movieid, genre)
SELECT movieid, genre FROM imdb_moviegenres;

-- Elimina la tabla antigua
DROP TABLE IF EXISTS imdb_moviegenres;

-- Renombra la tabla temporal para que tenga el nombre de la tabla original
ALTER TABLE imdb_moviegenres_temp RENAME TO imdb_moviegenres;


-- 3. Crea tabla temporal para los idiomas asociados a cada película
CREATE TABLE imdb_movielanguages_temp (
    language_id SERIAL PRIMARY KEY,
    movieid INTEGER NOT NULL,
    language CHARACTER VARYING(32) NOT NULL,
    FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON DELETE CASCADE
);

-- Inserta los datos existentes en la nueva tabla temporal
INSERT INTO imdb_movielanguages_temp (movieid, language)
SELECT movieid, language FROM imdb_movielanguages;

-- Elimina la tabla antigua
DROP TABLE IF EXISTS imdb_movielanguages;

-- Renombra la tabla temporal para que tenga el nombre de la tabla original
ALTER TABLE imdb_movielanguages_temp RENAME TO imdb_movielanguages;
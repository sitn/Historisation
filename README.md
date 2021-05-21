# Historisation

QGIS plugin to historize edited PostGIS data and archive it

Using this plugin enables the historisation of all changes made on PostGIS data,
might it be created, updated or deleted.

#### Make sure you read the wiki (in french) before proceeding as the user needs the right to write in the historisation configuration tables: https://github.com/sitn/Historisation/wiki
#### Merci de lire le wiki (en français) avant de continuer, car l'utilisateur doit avoir les droits d'écriture dans les tables de configuration de l'historisation: https://github.com/sitn/Historisation/wiki

## Initializing your database and the tables

Edit the `SEARCH_PATH` which corresponds to the PostgreSQL schema
where your table is.

```sql
SET SEARCH_PATH = "the_schema";


/* Table creation */
CREATE TABLE histo_param
(
    id            BIGSERIAL PRIMARY KEY,
    nom_table     VARCHAR(50) NOT NULL,
    display_field VARCHAR(50) NOT NULL,
    id_field      VARCHAR(50) NOT NULL
);
CREATE UNIQUE INDEX histo_param_nom_table_uindex
    ON histo_param (nom_table);

CREATE TABLE histo_event_type
(
    id          SMALLINT PRIMARY KEY,
    description VARCHAR(500)
);

CREATE TABLE histo_event
(
    id          BIGSERIAL PRIMARY KEY,
    event_date  TIMESTAMP   NOT NULL,
    author      VARCHAR(50) NOT NULL,
    type_id     SMALLINT    NOT NULL REFERENCES histo_event_type (id),
    description VARCHAR(500)
);

/* Initial value insertion */
INSERT INTO histo_event_type (id, description)
VALUES (0, 'Initialisation');
-- Add other value
```

Excute this first script, edit the second `SEARCH_PATH` value as well
and execute the here under script

```sql
SET SEARCH_PATH = "the_schema";

CREATE OR REPLACE FUNCTION create_h_table(schema text, source_table text, geometry_field text,
                                          code_fields text[]) RETURNS BOOLEAN AS
$$
DECLARE
    h_table    text;
    code_field text;
BEGIN
    h_table := schema || '.' || source_table || '_h';
    EXECUTE 'CREATE TABLE ' || h_table || ' AS SELECT * FROM ' || schema || '.' || source_table;

    EXECUTE 'ALTER TABLE ' || h_table || ' ADD histo_id bigserial NOT NULL';
    EXECUTE 'ALTER TABLE ' || h_table || ' ADD start_date timestamp';
    EXECUTE 'ALTER TABLE ' || h_table || ' ADD end_date timestamp';
    EXECUTE 'ALTER TABLE ' || h_table || ' ADD start_event_id bigint';
    EXECUTE 'ALTER TABLE ' || h_table || ' ADD end_event_id bigint';

    FOREACH code_field IN ARRAY code_fields
        LOOP
            EXECUTE 'ALTER TABLE ' || h_table || ' ADD ' || code_field || '_desc varchar(100)';
        END LOOP;

    EXECUTE 'ALTER TABLE ' || h_table || ' ADD CONSTRAINT ' || source_table || '_h_pk PRIMARY KEY(histo_id)';

    IF geometry_field <> '' THEN
        EXECUTE 'CREATE INDEX ' || source_table || '_h_' || geometry_field || ' ON ' || h_table ||
                ' USING gist(' || geometry_field || ')';
    END IF;

    RETURN TRUE;
END ;
$$
    LANGUAGE PLPGSQL
    EXTERNAL SECURITY DEFINER;
```

# Deploy

Clone this repository with the submodules, fetch all tags and checkout to a <TAG_NAME> of your choice

```
git fetch --all --tags --prune
git checkout tags/<TAG_NAME> -b <TAG_NAME>
```

Deploy to your custom repository

```
cd .\scripts
.\deploy.ps1
```

Tell users to delete the 2 caches if they don't see the new version:

`%APPDATA%\QGIS\QGIS3\profiles\default\cache`
`%LOCALAPPDATA%\QGIS\QGIS3\cache`

# Development mode

To easily develop and link the plugin, one should consider creating a linked folder between the QGIS Python plugin folder and the work/development folder. To do so, you can use a symlink:

    1. Create your working folder and link it to your Github repositories (something like c:/projects/historisation)
    2. Check the path to the Python plugin folder of QGIS (if on Windows 64bits, it would be somewhere like C:\Program Files\QGIS 3.16\apps\qgis\python\plugins)
    3. Open a command prompt as Administrator and run:

    mklink /D "c:\Program Files\QGIS 3.16\apps\qgis\python\plugins\Historisation" "c:\projects\historisation\Historisation"

Now you can develop in your working and tested it live in QGIS (using the plugin reloader).


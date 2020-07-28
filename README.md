# Historisation

QGIS plugin to historize edited PostGIS data and archive it

Using this plugin enables the historisation of all changes made on PostGIS data,
might it be created, updated or deleted.

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

Tell users to delete cache if they don't see the new version:

`%APPDATA%\QGIS\QGIS3\profiles\default\cache`



CREATE TABLE "job"(
    "id" INTEGER NOT NULL,
    "num_instruments" INTEGER NOT NULL
);
ALTER TABLE
    "job" ADD PRIMARY KEY("id");
CREATE TABLE "instrument"(
    "id" INTEGER GENERATED ALWAYS AS IDENTITY,
    "name" VARCHAR(255) NOT NULL,
    "job" INTEGER NOT NULL,
    CONSTRAINT fk_job
        FOREIGN KEY("job")
            REFERENCES "job"("id")
            ON DELETE CASCADE
);
ALTER TABLE
    "instrument" ADD PRIMARY KEY("id");

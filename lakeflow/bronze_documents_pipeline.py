"""Lakeflow Declarative Pipeline — incremental ingest of raw BPA scheme documents.

Auto Loader (`cloudFiles`) watches the Unity Catalog Volume where sponsor advisers'
scheme packs land and ingests each new file exactly once into a governed bronze
Delta table. Re-running the pipeline only picks up files that arrived since the last
run (checkpointed), so this is genuine incremental cloud-storage ingestion — not a
one-off batch read.

Deployed as a serverless Lakeflow pipeline targeting
`serverless_stable_wx20co_catalog.bpa_rubjit`.
"""
import dlt
from pyspark.sql import functions as F

VOLUME_PATH = "/Volumes/serverless_stable_wx20co_catalog/bpa_rubjit/documents"


@dlt.table(
    name="bronze_documents",
    comment="Raw BPA scheme documents incrementally ingested from the UC Volume via Auto Loader",
    table_properties={"quality": "bronze"},
)
def bronze_documents():
    raw = (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "binaryFile")
        .option("cloudFiles.includeExistingFiles", "true")
        .load(VOLUME_PATH)
    )
    # path looks like .../documents/<customer_slug>/<filename>
    rel = F.regexp_replace("path", r"^.*/documents/", "")
    customer_slug = F.split(rel, "/").getItem(0)
    filename = F.element_at(F.split("path", "/"), -1)
    ext = F.lower(F.element_at(F.split(filename, r"\."), -1))
    # doc kind from filename stem (mirrors server/extraction_schemas.classify_document_kind)
    doc_kind = (
        F.when(filename.rlike("(?i)benefit_spec"), "benefit_spec")
        .when(filename.rlike("(?i)bpa_data_pack"), "bpa_data_pack")
        .when(filename.rlike("(?i)triennial_valuation"), "triennial_valuation")
        .when(filename.rlike("(?i)funding_update"), "funding_update")
        .when(filename.rlike("(?i)summary_funding"), "summary_funding")
        .when(filename.rlike("(?i)contribution_schedule"), "contribution_schedule")
        .when(filename.rlike("(?i)member_data"), "member_data")
        .when(filename.rlike("(?i)investment_report"), "investment_report")
        .when(filename.rlike("(?i)cashflow"), "cashflow_projection")
        .when(filename.rlike("(?i)sip"), "statement_of_investment_principles")
        .when(filename.rlike("(?i)covenant"), "covenant_review")
        .when(filename.rlike("(?i)gmp"), "gmp_equalisation")
        .otherwise("other")
    )
    return (
        raw.select(
            F.col("path"),
            filename.alias("filename"),
            customer_slug.alias("customer_slug"),
            ext.alias("file_type"),
            doc_kind.alias("document_kind"),
            F.col("length").alias("size_bytes"),
            F.col("modificationTime").alias("source_modification_time"),
            F.current_timestamp().alias("ingest_time"),
        )
    )

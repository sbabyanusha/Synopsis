
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd

router = APIRouter()

@router.post("/gene_frequencies_from_supp/")
async def gene_frequencies_from_supp(
    clinical_file: UploadFile = File(...),
    mutations_file: UploadFile = File(None),
    cna_file: UploadFile = File(None),
    sv_file: UploadFile = File(None),
    genes: str = Form(...)
):
    try:
        genes = [gene.strip().upper() for gene in genes.split(",")]

        def parse(file):
            if file is None:
                return None
            df = pd.read_csv(file.file, sep="\t")
            df.columns = df.columns.str.strip().str.upper()
            return df

        clinical_df = parse(clinical_file)
        mut_df = parse(mutations_file)
        cna_df = parse(cna_file)
        sv_df = parse(sv_file)

        sample_col = next((col for col in clinical_df.columns if "SAMPLE" in col), "SAMPLE_ID")
        total_samples = clinical_df[sample_col].nunique()

        results = {}
        for gene in genes:
            mutation_samples = (
                mut_df[mut_df["HUGO_SYMBOL"] == gene]["TUMOR_SAMPLE_BARCODE"].nunique()
                if mut_df is not None and "HUGO_SYMBOL" in mut_df and "TUMOR_SAMPLE_BARCODE" in mut_df else 0
            )
            cna_samples = (
                cna_df[cna_df["HUGO_SYMBOL"] == gene]["SAMPLE_ID"].nunique()
                if cna_df is not None and "HUGO_SYMBOL" in cna_df and "SAMPLE_ID" in cna_df else 0
            )
            sv_samples = (
                sv_df[sv_df["HUGO_SYMBOL"] == gene]["SAMPLE_ID"].nunique()
                if sv_df is not None and "HUGO_SYMBOL" in sv_df and "SAMPLE_ID" in sv_df else 0
            )

            mut_profiled = mut_df["TUMOR_SAMPLE_BARCODE"].nunique() if mut_df is not None and "TUMOR_SAMPLE_BARCODE" in mut_df else 0
            cna_profiled = cna_df["SAMPLE_ID"].nunique() if cna_df is not None and "SAMPLE_ID" in cna_df else 0
            sv_profiled = sv_df["SAMPLE_ID"].nunique() if sv_df is not None and "SAMPLE_ID" in sv_df else 0

            results[gene] = {
                "mutation_frequency": round((mutation_samples / mut_profiled) * 100, 2) if mut_profiled else 0.0,
                "cna_frequency": round((cna_samples / cna_profiled) * 100, 2) if cna_profiled else 0.0,
                "sv_frequency": round((sv_samples / sv_profiled) * 100, 2) if sv_profiled else 0.0,
            }

        return {
            "total_samples": total_samples,
            "mutation_profiled": mut_profiled,
            "cna_profiled": cna_profiled,
            "sv_profiled": sv_profiled,
            "gene_frequencies": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

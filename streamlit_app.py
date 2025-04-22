
import streamlit as st
import requests

st.title("🧬 Gene Frequency + 📄 PDF Summarization + ❓ Q&A")

# --------- PDF Upload & Summarization Section ---------
st.header("📄 Upload PDF for Summarization & Q&A")
pdf_file = st.file_uploader("Upload a PDF file", type="pdf")

if pdf_file:
    if st.button("Summarize PDF"):
        with st.spinner("Summarizing..."):
            response = requests.post(
                "http://localhost:8002/summarize_pdf/",
                files={"file": (pdf_file.name, pdf_file, "application/pdf")}
            )
        if response.ok:
            summary = response.json()["summary"]
            st.subheader("📋 Summary")
            st.write(summary)
        else:
            st.error("Failed to summarize the PDF.")

    st.subheader("❓ Ask a question based on this PDF")
    question = st.text_input("Enter your question")
    if st.button("Ask Question") and question:
        with st.spinner("Generating answer..."):
            ingest_response = requests.post(
                "http://localhost:8002/ingest_pdf/",
                files={"file": (pdf_file.name, pdf_file, "application/pdf")}
            )
            if ingest_response.ok:
                answer_response = requests.post(
                    "http://localhost:8002/generate_evidence/",
                    data={"question": question}
                )
                if answer_response.ok:
                    answer = answer_response.json()["answer"]
                    st.markdown("### 💡 Answer")
                    st.write(answer)
                else:
                    st.error("Failed to generate an answer.")
            else:
                st.error("Failed to ingest the PDF for context.")

# --------- Gene Frequency Analysis Section ---------
st.header("🧬 Gene Frequency Analysis from Supplement Files")

mut_file = st.file_uploader("Upload data_mutations.txt", type="txt", key="mut")
cna_file = st.file_uploader("Upload data_cna.txt", type="txt", key="cna")
sv_file = st.file_uploader("Upload data_sv.txt", type="txt", key="sv")
clin_file = st.file_uploader("Upload data_clinical_sample.txt", type="txt", key="clin")

genes = st.text_input("Enter genes to search for (comma-separated, e.g., TP53, BRCA1, EGFR)")

if st.button("Analyze Gene Frequencies") and clin_file and genes:
    files = {
        "clinical_file": ("data_clinical_sample.txt", clin_file, "text/plain"),
    }
    if mut_file: files["mutations_file"] = ("data_mutations.txt", mut_file, "text/plain")
    if cna_file: files["cna_file"] = ("data_cna.txt", cna_file, "text/plain")
    if sv_file: files["sv_file"] = ("data_sv.txt", sv_file, "text/plain")

    response = requests.post(
        "http://localhost:8002/gene_frequencies_from_supp/",
        data={"genes": genes},
        files=files,
    )

    if response.ok:
        result = response.json()
        st.subheader("📊 Study Summary")
        st.markdown(f"- Total samples: **{result['total_samples']}**")
        st.markdown(f"- Mutation profiled samples: **{result['mutation_profiled']}**")
        st.markdown(f"- CNA profiled samples: **{result['cna_profiled']}**")
        st.markdown(f"- SV profiled samples: **{result['sv_profiled']}**")

        st.subheader("🎯 Gene Alteration Frequencies")
        for gene, freqs in result["gene_frequencies"].items():
            st.markdown(f"**{gene}**:")
            st.markdown(f"- Mutation: {freqs['mutation_frequency']}%")
            st.markdown(f"- CNA: {freqs['cna_frequency']}%")
            st.markdown(f"- SV: {freqs['sv_frequency']}%")
    else:
        st.error(f"❌ Failed to fetch gene frequency results: {response.status_code}")
        st.text(response.text)

import PyPDF2
from gliner import GLiNER
import warnings

# Ignore specific warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Function to extract text from the PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text 


def extract_entities(text, labels, model):

    # Use GLiNER to extract entities
    entities = model.predict_entities(text, labels)

    # Organize the entities into a dictionary
    entities_ref = []
    for entity in entities:
        entities_ref.append({entity["label"]: entity["text"]})
    return entities_ref

if __name__ == "__main__":
    # Path to the PDF file
    pdf_path = "./data/agendaTest.pdf"

    # Step 1: Extract the text from the PDF
    #extracted_text = extract_text_from_pdf(pdf_path)
    #print("Extracted Text:\n", extracted_text)

    extracted_text = "Augusto Heleno, Ministro-Chefe do Gabinete de Segurança Institucional da Presidência da República; e Deputado Major Vitor Hugo (PSL/GO), Líder do Governo na Câmara dos Deputados"
    extracted_text = "Augusto Heleno, Chief Minister of the Office of Institutional Security of the Presidency of the Republic;"
    y = "and Deputy Major Vitor Hugo (PSL/GO), Leader of the Government in the Chamber of Deputies"
    model = GLiNER.from_pretrained("urchade/gliner_multi")


    # Step 2: Define the entity labels you want to extract
    labels = ["person", "party", "position title"]

    # Step 3: Extract the entities using GLiNER
    entities=  extract_entities(extracted_text+y, labels, model)

    # Step 4: Print the extracted entities
    print("\nExtracted Entities:")
    for extraccted in entities:
        for label, entity in extraccted.items():
            print(f"{label}: {entity}")

# Notebooks

The research behind the app, kept as it was run, outputs included. File paths in them point at the original project
folders (`Brahmi2/`, `Modi/`, `OCR/`); the data they read is in the
[Kaggle dataset](https://www.kaggle.com/datasets/paragtonpe/brahmi-ocr-synthetic-dataset).

| Notebook | What it does |
|---|---|
| [brahmi_dataset.ipynb](brahmi_dataset.ipynb) | Lists the Brahmi characters in the Noto Sans Brahmi font and renders 10,000 synthetic lines of one to seven characters, with their labels. |
| [brahmi_crnn.ipynb](brahmi_crnn.ipynb) | Trains the CRNN (CNN, two-layer bidirectional LSTM, CTC loss) in PyTorch, measures the character error rate and exports the model to ONNX. This is the model the app uses. |
| [brahmi_image_testing.ipynb](brahmi_image_testing.ipynb) | Thresholding, contour finding and skeletonising photos of Brahmi text. |
| [image_preprocessing.ipynb](image_preprocessing.ipynb) | Lighting correction, contrast enhancement and denoising for inscription photos, then character segmentation and recognition. |
| [iast_translation.ipynb](iast_translation.ipynb) | The first version of IAST to English with a word list and a dictionary. |

`experiments/` holds earlier attempts that the app no longer uses: a character classifier (CNN), a TensorFlow CRNN
that did not learn (its error rate stayed above 90%), and the first drafts of Brahmi and Modi transliteration. The
drafts contain the mapping errors fixed in version 1.0.0; the code in `brahmi_modi/` is the corrected version.

## Running them

They need more than the app: PyTorch and torchvision, TensorFlow, pandas, scikit-learn, scikit-image, OpenCV,
fontTools, matplotlib and ONNX Runtime. The dataset notebook also needs the
[Noto Sans Brahmi](https://fonts.google.com/noto/specimen/Noto+Sans+Brahmi) font file.

To reproduce the result in the README, the held-out lines are the 20% split made by
`train_test_split(metadata, test_size=0.2, random_state=42)` on the dataset's `metadata.csv`, as in
`brahmi_crnn.ipynb`.

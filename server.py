#!/usr/bin/env python3
from flask import Flask, request, jsonify
import pytext

config_file = "joint-model.json"
model_file = "joint_model.c2"

config = pytext.load_config(config_file)
predictor = pytext.create_predictor(config, model_file)

app = Flask(__name__)

label_threshold = 0.1

@app.route("/chat", methods=['GET', 'POST'])
def chat():
  message = request.data.decode()
  result = predictor({"raw_text": message})
  
  best_doc_label = max(
        (label for label in result if label.startswith("doc_scores:")),
        key=lambda label: result[label][0],
  )[len("doc_scores:"):]
  
  best_label = max(
        (label for label in result if label.startswith("word_scores:") and label != "word_scores:NoLabel"),
        key=lambda label: result[label],
  )

  best_label_score = result[best_label][0]
  labels = []
  for label in result:
    if label.startswith("word_scores:") and label != "word_scores:NoLabel" and best_label_score - result[label][0] <= label_threshold:
      labels.append(label[len("word_scores:"):])
 
  if best_doc_label == "product":
    return jsonify({"answer": f"Are you asking about {best_doc_label} {labels}?"})
  elif best_doc_label == "add":
    return jsonify({"answer": f"Product was added to your cart"})
  elif best_doc_label == "cost":
    return jsonify({"answer": f"We calculate price for you"})
    
  return jsonify({"answer": f"Sorry could you repeat please."})


app.run(host='0.0.0.0', port='8080', debug=True)


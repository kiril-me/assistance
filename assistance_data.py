#!/usr/bin/env python3

import re
import os
import random
import click

VALIDATION_SPLIT = 0.20
TEST_SPLIT = 0.10
SLOT_PATTERN = re.compile(r"\(([^)]+)\)\[([^\]]+)\]") #

def write_to_file(output_directory, name, list):
  file_name = os.path.join(output_directory, name)
  with open(file_name, "w") as f:
    for (intent, slots, text) in list:
      slots_string = ','.join([ str(st) + ":" + str(en) + ":" + slt  for (slt, st, en) in slots])
      f.write(intent + "\t" + slots_string + "\t" + text + "\n")

def parseText(text):
  slots = []
  replace_slots = []

  search_start = 0
  chars_removed = 0
  normalize_text = "BOS "
  intend = len(normalize_text)

  while True:
    match_result = SLOT_PATTERN.search(text, search_start)
    if match_result:
      value = match_result.group(1)
      group_start = match_result.span(0)[0]
      group_end = match_result.span(0)[1]

      replace_slots.append((value, group_start, group_end))

      label = match_result.group(2)
      label_start = group_start - chars_removed + intend

      slots.append((label, label_start, label_start + len(value)))

      chars_removed += len(match_result.group(0)) - len(value)
      search_start = group_end
    else:
      break


  last_change = 0
  for (label, start, end) in replace_slots:
    normalize_text += text[last_change:start] + label
    last_change = end

  normalize_text += text[last_change:len(text)]
  normalize_text += " EOS"

  return (slots, normalize_text)


def readFromFile(file_name):
  dataset = []
  with open(file_name, "r") as file:
    for line in file:
      line = line.rstrip('\n')
      columns = re.split(r"\t| ", line, 1)#.split("\t", 1)
      (slots, normalize_text) = parseText(columns[1])
      dataset.append((columns[0], slots, normalize_text))

  return dataset


def readFromConsole():
  dataset = []
  work = True
  while work:
    try:
      intent = input("Intent: ")
      if len(intent) == 0:
        break;

      text = input("Text: ")
      if len(text) == 0:
        break;
    except EOFError:
      break

    (slots, normalize_text) = parseText(text)
    dataset.append((intent, slots, normalize_text))
    print("") # just to visualy separate

  return dataset


@click.command()
@click.option("-t", "--text-file", required=False, type=str)
@click.option("-o", "--output-directory", required=True, type=str)
@click.option("-v", "--verbose", default=False, type=bool)
def main(text_file, output_directory, verbose):
  print("Start making your assistance dataset")

  if text_file is None or len(text_file) == 0:
    dataset = readFromConsole()
  else:
    dataset = readFromFile(text_file)

  random.shuffle(dataset)

  size = len(dataset)
  if size  < 100:
   train_set = dataset
   val_set = dataset
   test_set = dataset
  else:
    train_split = int(size * (1.0 - VALIDATION_SPLIT - TEST_SPLIT))
    val_slit = train_split + int(size * VALIDATION_SPLIT)

    train_set = dataset[0:train_split]
    val_set = dataset[train_split:val_slit]
    test_set = dataset[val_slit:size]

  write_to_file(output_directory, "train.csv", train_set)
  write_to_file(output_directory, "val.csv", val_set)
  write_to_file(output_directory, "test.csv", test_set)

  print("Processing finsihed")

if __name__ == "__main__":
    main()




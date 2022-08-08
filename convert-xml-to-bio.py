#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import re
from nltk.tokenize import sent_tokenize, word_tokenize


# In[2]:


# label conversion options
convert_labels = True
label_conversion_list = {
    'subject':'SUB',
    'subject.reference':'SUB',
    
    'coverage.temporal':'PER',
    'coverage.temporal.reference':'PER',
    'date.event':'PER',
    'date.publication':'PER',
    
    'coverage.spatial.placename':'LOC',
    'coverage.spatial.placename.reference':'LOC'
}

# output options
token_label_separator = ' \t' # doccano expects space + tab for sep!

# define input/output folders
ariadne_folder = "D:\\phd-data\\NER-annotation-data\\English\\Ariadne-dataset-annotated\\Training&TaggedSample\\training-other\\"
output_folder = "D:\\phd-data\\NER-annotation-data\\English\\Ariadne-dataset-annotated\\doccano-formatted\\training-other\\"

# define regex for matching 1 or more spaces
regex_spaces = r"[ ]+"

# define regex for matching 1 or more line endings
regex_lineendings = r"[\n]+"
regex_lineendings_with_space = r"[\n]+ ?[\n]+"

# define regex for matching tags
regex_tag_start = r"\<([a-z.]+)\>"
regex_tag_end = r"\<\/([a-z.]+)\>"


# In[3]:


#all_tags = {}

for filename in os.listdir(ariadne_folder):
    
    file_path = os.path.join(ariadne_folder, filename)
    
    with open(file_path) as f:
        
        text = f.read()
        #print(text[0:200])
        
        # remove line endings
        text = text.replace('\n',' ')
        
        # replace multiple spaces with one space
        text = re.sub(regex_spaces, " ", text, 0, re.MULTILINE)
        #print(text[0:200])
        
        # sentence detection / tokenisation
        tokens_sentences = [word_tokenize(t) for t in sent_tokenize(text)]
        
        # re-assemble the tags
        tokens_sentences_with_fixed_tags = []
        
        for sentence in tokens_sentences:
            
            tokens_with_fixed_tags = []
            in_tag = False
            fixed_tag = ''
            
            for token in sentence:
                
                # start of tag, start collecting tokens
                if token == '<':
                    in_tag = True
                    fixed_tag = token
                    
                # end of tag, add collected tokens to output list
                elif in_tag and token == '>':
                    fixed_tag += token
                    tokens_with_fixed_tags.append(fixed_tag)
                    fixed_tag = ''
                    in_tag = False
                
                # middle of tag, add to fixed_tag
                elif in_tag:
                    fixed_tag += token
                
                # normal token, add to output list
                else:
                    tokens_with_fixed_tags.append(token)
            
            # add fixed tags tokens to output
            tokens_sentences_with_fixed_tags.append(tokens_with_fixed_tags)
                    
        
        #print(tokens_sentences_with_fixed_tags[0:500])
        #exit()
        
        
        # loop through sentences/tokens, and add to output in BIO format
        
        output = ''
        in_tag = False
        first_token_in_tag = False
        
        for sentence in tokens_sentences_with_fixed_tags:
            for token in sentence:
                
                # start tag, extract it
                if re.match(regex_tag_start, token):
                    tag = re.search(regex_tag_start, token).group(1)
                    #all_tags[tag] = 1
                    if tag in label_conversion_list:
                        tag = label_conversion_list[tag]
                        in_tag = True
                        first_token_in_tag = True

                # end tag, stop adding B/I
                elif re.match(regex_tag_end, token):
                    in_tag = False

                # we're within a tag, add B/I
                elif in_tag:
                    if first_token_in_tag:
                        output += f"{token}{token_label_separator}B-{tag}\n"
                        first_token_in_tag = False
                    else:
                        output += f"{token}{token_label_separator}I-{tag}\n"

                # token outside of tags, just add to output
                else:
                    output += f"{token}{token_label_separator}O\n"

            
            # at the end of each 'sentence', if not within a tag, add a sentence separator. if in tag, merge two sentences
            if not in_tag:
                output += '\n'
        
        
        #print(output)
        
        # save BIO file
        output_path = os.path.join(output_folder, filename)
        with open(output_path, 'w') as f:
            f.write(output)
        

#print(all_tags)


# In[ ]:





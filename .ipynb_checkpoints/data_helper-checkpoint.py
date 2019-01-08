import re
import os
import pickle

def using_split_old(line, _len=len):
    words = line.split()
    index = line.index
    offsets = []
    append = offsets.append
    running_offset = 0
    for word in words:
        word_offset = index(word, running_offset)
        word_len = _len(word)
        running_offset = word_offset + word_len
        append((word, word_offset, running_offset))
    return offsets

def using_split_current(line, _len=len):
    '''
    This split method differs from the original split method in that this 
    handles special chars such as \n ,
    '''
    words = line.split()
    index = line.index
    offsets = []
    append = offsets.append
    running_offset = 0
    
    for word in words:
        word_offset = index(word, running_offset)
        word_len = _len(word)
        
        if '¤' in word or "¶" in word or '∞' in word or 'ª' in word:
            s_words = re.split("([¤,¶,∞,ª])", word)
            s_running_offset = running_offset
                    
            for s_word in s_words: 
                s_word_offset = index(s_word, s_running_offset)
                s_word_len = _len(s_word)
                s_running_offset = s_word_offset + s_word_len
                if len(s_word)>0:
                    append((s_word, s_word_offset, s_running_offset))
            running_offset = word_offset + word_len
        else:
            running_offset = word_offset + word_len
            append((word, word_offset, running_offset))
    return offsets

def preprocess_text(text_in):
    text = str(text_in).lower()
    text = text.replace('.',' ')
    text = text.replace(':',' ')
    text = text.replace('-',' ')
    text = text.replace('_',' ')
    text = text.replace('*',' ')
    #New additions
    text = text.replace(';',' ')
    text = text.replace('(',' ')
    text = text.replace(')',' ')
    text = text.replace('[',' ')
    text = text.replace(']',' ')
    text = text.replace('#',' ')
    text = text.replace('+',' ')
    text = text.replace('%',' ')
    text = text.replace('\n','¤')
    text = text.replace('/','¶')
    text = text.replace('.','∞')
    text = text.replace(',','ª')
    text = text.replace('\\','ª')
    
    return text

def get_files(folder):
    cur_files = []
    for root, dirs, files in os.walk(folder):  
        cur_files = files      
    
    cur_files = [f for f in cur_files if not f[0] == '.']
    return cur_files

def process_tag_file_multiple(cur_tag_file):
    '''
    Process multiple tags in a file
    '''
    file_name = ''
    cui = ''
    locations = []
    
    lines = open(cur_tag_file,'r').readlines()
    for line in lines:
        line = line.strip()
        parts = line.split("||")
        file_name = parts[0]
        cui = parts[2]
        temp = parts[3:]
        for i in range(0, len(temp), 2):
            locations.append((cui, int(temp[i]),int(temp[i+1])))
    return(file_name,locations)

def process_tag_file_single_only(cur_tag_file):
    '''
    This method differs from the origin method in which all disorder tokens were extracted.
    This new method will ignore any disorder lines that contains more than 2 tokens.
    '''
    file_name = ''
    cui = ''
    locations = []
    print(cur_tag_file)
    lines = open(cur_tag_file,'r').readlines()
    for line in lines:
        line = line.strip()
        parts = line.split("||")
        file_name = parts[0]
        cui = parts[2]
        temp = parts[3:]
        if len(temp) < 3:
            for i in range(0, len(temp), 2):
                locations.append((cui, int(temp[i]),int(temp[i+1])))
    return(file_name,locations)


def convert_to_bio_format(working_folder, tags_dict_path, bio_output):
    file = open(tags_dict_path,'rb')
    tags_dict = pickle.load(file)
    file.close()
    
    cur_files = get_files(working_folder)
    for c_file in cur_files:
        c_file_path = working_folder+c_file
        
        cur_list_of_tag=[]
        try:
            cur_list_of_tags = tags_dict[c_file]
        except:
            pass
        
        print(c_file)
        #cur_dict_of_tags = {b:c for a,b,c in cur_list_of_tags}
        #print(cur_dict_of_tags)
        text = ''
        with open(c_file_path, 'r') as myfile:
            text=myfile.read()
        text = preprocess_text(text)
        tokens = using_split_current(text)
        with open(bio_output+c_file,'w') as writer:
            for token in tokens:
                cui_str = token[0]
                token_start = token[1]
                token_end = token[2]
                cur_tag = 'O'

                for tag in cur_list_of_tags:
                    ref_start = tag[1]
                    ref_enbd = tag[2]
                    if ref_start <= token_start <= ref_enbd:
                        if ref_start <= token_end <= ref_enbd:
                            if token_end - token_start > 0:
                                cur_tag = "Disorder"
                #new_token = (cui_str,token_start,token_end,cur_tag)
                #print(new_token)
                writer.write("%s\t%s\t%s\t%s\n" % (cui_str,token_start,token_end,cur_tag))
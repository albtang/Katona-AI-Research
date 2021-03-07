import json
import os
import numpy as np
import tensorflow as tf
import model, sample, encoder
import pandas as pd
from collections import defaultdict
import re

#interactive mode: input prompt and test out the AI.
#non-interactive mode: use a list of prompts to generate a large number of responses to each prompt.
#generate_responses: bgn_prompt--the beginning phrase in each prompt
#                    end_prompt--the ending phrase in each prompt
#                    brand_list--the list of brands used in these prompts
#                    nsample--the number of samples generated for each prompt
#                    model_size--the size of the gpt2 model. we mostly use the 345M version.
#process_responses: all_text: responses generated by generate_responses
#                   keywords: the list of keywords the program searches for in each of the provided responses.
def interact_model(
    model_name,
    seed,
    nsamples,
    batch_size,
    length,
    temperature,
    top_k,
    models_dir
):
    models_dir = os.path.expanduser(os.path.expandvars(models_dir))
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name, models_dir)
    hparams = model.default_hparams()
    with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)

        while True:
            raw_text = input("Model prompt >>> ")
            if raw_text=="end":
                break
            while not raw_text:
                print('Prompt should not be empty!')
                raw_text = input("Model prompt >>> ")
            context_tokens = enc.encode(raw_text)
            generated = 0
            for _ in range(nsamples // batch_size):
                out = sess.run(output, feed_dict={
                    context: [context_tokens for _ in range(batch_size)]
                })[:, len(context_tokens):]
                for i in range(batch_size):
                    generated += 1
                    text = enc.decode(out[i])
                    print("=" * 40 + " SAMPLE " + str(generated) + " " + "=" * 40)
                    print(text)
            print("=" * 80)

def noninteract_model(
    model_name,
    seed,
    nsamples,
    batch_size,
    length,
    temperature,
    top_k,
    models_dir,
    prompt_list
):
    models_dir = os.path.expanduser(os.path.expandvars(models_dir))
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name, models_dir)
    hparams = model.default_hparams()
    with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)
        all_text={}
        for prpt in prompt_list:
            print(prpt)
            text_list=[]
            raw_text = prpt
            context_tokens = enc.encode(raw_text)
            generated = 0
            for _ in range(nsamples // batch_size):
                out = sess.run(output, feed_dict={
                    context: [context_tokens for _ in range(batch_size)]
                })[:, len(context_tokens):]
                for i in range(batch_size):
                    generated += 1
                    text_list.append(enc.decode(out[i]))
            all_text[prpt]=text_list
    return all_text

#auxilary functions used to generate and process sample responses
def generate_responses(bgn_prompt,end_prompt, brand_list, nsample,model_size):
    prompt_list=[]
    for brand in brand_list:
        prompt_list.append(bgn_prompt+brand+end_prompt)
    return noninteract_model(
    model_size,
    None,
    nsample,
    1,
    300,
    0.5,
    0,
    '../models',
    prompt_list
)

def process_responses(all_text,keywords,filename):
    all_text = pd.DataFrame(all_text)
    all_text.to_csv('gender_data/raw_text/'+filename+'.csv')
    frqs = {}
    for prompt in all_text.columns:
        frqs[prompt] = {}
        series = all_text[prompt].str.split("<|endoftext|>", expand=True)[0]
        for brand in keywords:
            cnt = pd.Series(np.zeros_like(series))
            for alias in brand:
                cnt = cnt | series.str.contains('[^A-z]' + alias + '[^A-z]', case=False)
            frqs[prompt][brand[0]] = cnt.sum()
    pd.DataFrame(frqs).to_csv('gender_data/freqs/'+filename+'.csv')

car_aliases = [['Jeep', 'Fiat', 'Chrysler'],
        ['Subaru', 'Bugeye', 'Scooby'],
        ['Dodge', 'Polara'],
#        ['GMC'],
        ['Tesla'],
#        ['Buick'],
        ['Toyota', 'Yota', 'Camry'],
        ['Honda', 'Accord'],
        ['Nissan', 'Infiniti'],
        ['Chevrolet', 'Chevy'],
        ['Hyundai', 'Tiburon', 'HYU', 'Kia'],
#        ['Ram'],
        ['Mazda', 'Matsuda'],
        ['Renault', 'Dacia'],
        ['Lamborghini', 'Lambo', 'Aventadora', 'Lamborgini'],
        ['Mercedes-Benz', 'Merc', 'Benz', 'Mercedes'],
        ['BMW', 'Beemer', 'Bimmer', 'Beamer'],
        ['Ford', 'Thunderbird', 'Mustang'],
        ['Porsche', 'Porche', 'Porce'],
        ['Audi', '4 Rings'],
        ['Volkswagen', 'VW', 'Volkswagon'],
        ['Ferrari', 'Prancing Horse', 'Scuderia'],
#        ['MG', 'M.G.', 'Morris Garages', 'M.G. Car Company'],
        ['Lexus', 'Lex', 'GX', 'ES 250'],
#        ['Infiniti'],
        ['Volvo']]

beer_aliases = [['Red Stripe'],
        ['Rolling Rock'],
        ['Bud Light'],
        ['Coors Light', 'Coors'],
        ['Sam Adams'],
        ['Budweiser'],
        ['Miller Lite'],
        ['Corona Extra'],
        ['Heineken'],
        ['Michelob Ultra'],
        ['Modelo Especial', 'Modelo'],
        ['Busch Light'],
        ['Natural Light', 'Natty Light', 'Natty'],
        ['Busch'],
        ['Miller High Life'],
        ['Keystone Light'],
        ['Stella Artois'],
        ['Pabst Blue Ribbon', 'PBR'],
        ['Bud Ice'],
        ['Natural Ice'],
        ['Blue Moon', 'Blue Moon Belgian White'],
        ['Yeungling Lager'],
        ['Dos Equis'],
        ['Steel Reserve'],
        ['Coors Banquet'],
        ['Corona Light'],
        ['Guiness'],
        ["Milwaukee's Best Ice"]]

gender_aliases = [
        ['Male', 'Man', 'Mr', 'mister', 'he', 'him', 'his', 'men', 'gentleman', 'gentlemen', 'males', 'sir', 'boy', 'guy', 'boys', 'guys'],
        ['Female', 'Woman', 'Mrs', 'Ms', 'she', 'her', 'hers', 'women', 'lady', 'ladies', 'gentlelady', 'gentleladies', 'females', "ma'am", 'madam', 'girl', 'gal', 'girls', 'gals']]

process_responses(generate_responses(""," think Mercedes-Benz is similar to",gender_aliases[0]+gender_aliases[1],100,"345M"), gender_aliases, 'b Feb26 100 10')



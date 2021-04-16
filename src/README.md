# Generating data with GPT-2
Currently, text generation is performed by running `gpt2_with_regex.py`. `gpt2_working_version_9_20_peiyao.py` was the starting point, before it became deprecated when we switched to a regex approach to counting the frequency of words. `gpt2_params_change.py` is largely the same as `gpt2_with_regex.py` with the exception being the hyperparameters (e.g. top_k, temperature) may be modified. It also does not have the latest parsing algorithm, which may result in slightly skewed frequency counts. If you intend to experiment with hyperparameters in the future, make sure to copy the new parsing algorithm from `process_responses()` in `gpt2_with_regex.py`.

Most of the time, you'll only need to change the sequence number on the file name on the last line of the file when generating a batch. Below, I'll be breaking down the important bits of `gpt2_with_regex.py`.

### Aliases
We format aliases as a list of lists. Each brand occupies its own list, with the brand name first and its alises following it. For example, here's a sample of the `car_aliases`:
```
car_aliases = [['Jeep', 'Fiat', 'Chrysler'],
        ['Subaru', 'Bugeye', 'Scooby'],
        ...
        ['Volvo']]
```
This format is needed for `process_responses()` to operate without modification. It also allows for `generate_responses()` to get the list of brand names to create prompts from very easily using `[i[0] for i in {aliases}]`.

### `generate_responses()`
Function parameters:
- `bgn_prompt`: String
- `end_prompt`: String
- `brand_list`: List of Strings
- `nsample`: Int
- `model_size`: String. We have been exclusively using "345M" so far, but you can download other models from running `download_model.py`

Returns:
- `all_text`: Dictionary where Key = prompt, Value = text generated

Each prompt is then added together as `bgn_prompt + brand + end_prompt`, where `brand` is each element of `brand_list`. Each prompt is run for `nsample` times.

For example, if I wanted generate 10 samples from the prompt "The car brand Mercedes-Benz is similar to", I would use `generate_responses("The car brand ", " is similar to", ["Mercedes-Benz"], 10, "345M")`. If I wanted generate 10 samples from the prompt "Mercedes-Benz is similar to", I would use `generate_responses("", " is similar to", ["Mercedes-Benz"], 10, "345M")`.

When running baseline samples, i.e. when not including a brand in the prompt and just the category, `brand_list` should be `[""]`. Using `[]` will result in no prompt being generated, and thus no samples collected. An example usage would be `generate_responses("The car brand", " is similar to", [""], 10, "345M")`.

### `process_responses()`

TODO

## Using screen to run concurrent samples
TODO
## Vim Tricks
TODO

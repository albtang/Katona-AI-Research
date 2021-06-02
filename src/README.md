# Generating data with GPT-2
Currently, text generation is performed by running `gpt2_with_regex.py`. `gpt2_working_version_9_20_peiyao.py` was the starting point, before it became deprecated when we switched to a regex approach to count the frequency of words. `gpt2_params_change.py` is largely the same as `gpt2_with_regex.py` with the exception being the hyperparameters (e.g. top_k, temperature) may be modified. It also does not have the latest parsing algorithm, which may result in slightly skewed frequency counts. If you intend to experiment with hyperparameters in the future, make sure to copy the new parsing algorithm from `process_responses()` in `gpt2_with_regex.py`.

Most of the time, you'll only need to change the sequence number on the file name on the last line of the file when generating a batch. Below, I'll be breaking down the important bits of `gpt2_with_regex.py`.

### Aliases
We format aliases as a list of lists. Each brand occupies its own list, with the brand name first and its aliases following it. For example, here's a sample of the `car_aliases`:
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

For example, if I wanted to generate 10 samples from the prompt "The car brand Mercedes-Benz is similar to", I would use `generate_responses("The car brand ", " is similar to", ["Mercedes-Benz"], 10, "345M")`. If I wanted to generate 10 samples from the prompt "Mercedes-Benz is similar to", I would use `generate_responses("", " is similar to", ["Mercedes-Benz"], 10, "345M")`.

When running baseline samples, i.e. when not including a brand in the prompt and just the category, `brand_list` should be `[""]`. Using `[]` will result in no prompt being generated, and thus no samples collected. An example usage would be `generate_responses("The car brand", " is similar to", [""], 10, "345M")`.

### `process_responses()`

Function parameters:
- `all_text`: Dictionary from `generate_responses` or equivalent that can be made into a DataFrame
- `keywords`: List of lists of Strings
- `filename`: String

*Note: This function hard codes what folder (e.g. `beer_data`) to save data to in two locations.*

This function creates a DataFrame out of `all_text` and then parses it for each brand alias in `keywords`. It then saves the raw text and frequency CSVs under the `filename`.

This usually takes the return value of `generate_responses`. An example usage is:
```
process_responses(generate_responses(""," is similar to",[i[0] for i in beer_aliases],50,"345M"), beer_aliases, 'Apr23 50 15')
```

## Using _screen_ to run concurrent samples
Running multiple scripts on the same server requires multiple terminals. We could use multiple SSH sessions, but it's simpler to use _screen_ to accomplish the same thing.

Everything I know is from: https://www.howtogeek.com/662422/how-to-use-linuxs-screen-command/ Here are the important commands:
- `screen -ls` - Lists the named screens.
- `screen -S {name}` - Creates a saved _screen_ under the name.
- `screen -r {name}` - Resumes a saved _screen_ under the name.
- `Ctrl+A`, then `D` - Detaches from a _screen_.

What I typically do is login via SSH. I run `git pull` in the repo directory to pull any changes. Then I access the _screens_ via `screen -r sim1`, change the output filenames in the python file via _vim_ (`vim gpt2_with_regex.py`), and then run the script via `python gpt2_with_regex.py`. Then detach via `Ctrl+A`, then `D`, and then repeat on the next screen.
## Vim Tricks
Vim is an inline code editor, necessary for editing files while SSH'd in. It has a lot of features I've never used, but here are the basics:
- Use `vim {file}` to run vim on that file.
- Once you're in, you're able to use the arrows to navigate.
- `i` sets you into insert mode, so you'll be able to delete and insert text.
- `r` followed by a letter will replace the letter in front of the cursor with the typed letter. This is best used for modifying the sequence number when running multiple things at once.
- Once you're done editing, press `esc` to exit insert mode.
- To save and exit, type `:wq`. Make sure you are no longer in insert mode.
- If you want to exit, type `:q`. If there are changes, it'll warn you. You can exit without saving via `:q!`.

## Further Improvements
- Refactor `gpt2_with_regex.py` so that you can specify the output folder and filenames via the command line. Alternatively, have them in one location in the file that you can edit in one go.
- Centralize the merger and parser notebooks instead of having them distributed across the individual data folders.

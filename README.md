## Replication Package 
# From Developer Pairs to AI Copilots: A Comparative Study on Knowledge Transfer

## Contents and Structure

- *assignment*

    Contains two versions of the project folder participants received before starting the session, including a document explaining the task.

    - *blank*

        The project folder the participants received with functions that are to be completed are marked with "# TODO' (only in *db.py*).

    - *solution*

        The same project folder, but with a sample solution filled in at the '# TODO' comments.

- *material*

    Contains several documents that were used during the study.

    - *instructions.pdf*

        The instructions that were read to the participants before they were allowed to start programming.

    - *questionnaire_consent.pdf*

        The pre-test questionnaire the participants filled *and* the consent form they were required to sign.

- *plots*
    
    Contains all the plots from the paper. They were generated using the scripts in *scripts/evaluation*.

- *results*

    Contains the raw results from the evaluation (see *scripts/evaluation*).

    - *agg*

        Contains the aggregated data from all transcripts and for each session (i.e. the length and depth of all episodes).

    - Various .csv files

        Statistical evaluations and/or counts of several features.

- *scripts*

    Contains several Python scripts used for evaluation and annotation.

    To run the scripts, please refer to the --help command.

    - *annotation*
        - *colors.py*

            A helper script
        
        - *transcriptor.py*

            The annotation tool. A console application that allows interactive annotation of the transcripts. Results are stored in *transcripts/final*.

    - *conversion*
        - *convert_to_audio.sh*
            
            Some audio files were in the .ogg format. As the OpenAI API requires .mp3 input, this script converts .ogg files to .mp3.
        
        - *openai_interface.py*

            Script that uploads an .mp3 file to the OpenAI Whisper model and writes its output into a file. Our outputs are located in *transcripts/single*.

        - *pipeline.py* 

            Calls all the necessary preprocessing scripts in the correct order, such that we only have to run one script.

        - *preprocess.py*

            Merges the 3 output files from OpenAI Whisper into one text file, adds line breaks after each sentence, and removes filler words.

        - *split_audio.py*

            Cuts the audio files into three parts that are at max 20min long, since this is the maximum length the OpenAI API will accept.

    - *evaluation*
        - *aggregate.py*
            
            Reads all the .json output files from the annotation and aggregates the data. Results are stored in *results/agg*.
            This script is called by *scripts/evaluation/eval.py* when passed the respective parameters.
            
        - *constants.py*

            Helper script that defines all the dict keys necessary to read the transcript files.

        - *eval.py*

            Main evaluation script that calls the respective functions for a specific evaluation.

        - *plots.py*

            Creates the plots displayed in the paper.
            Relies on the outputs from the evaluation script.

        - *stats.py*

            Collects statistics and performs statistical tests associated with the following data:
            - episode-frequency: Number of episodes
            - episode-length-depth: Length and depth of episodes
            - topics: Distribution of episode topics
            - finish-types: Distribution of episode finish types

            This script is called by *scripts/evaluation/eval.py* when passed the respective parameters.

        - *questionnaire.py*

            Evaluates the questionnaire data.

        - *util.py* 

            Useful helper functions for the evaluation.

- *transcripts*
    - *final*

        The processed transcript files (.txt) and the annotated .json files.
    
    - *single*

        Raw audio transcript files; 3 parts for each session

## Statistical Tests

This section provides a brief overview over the statistical tests performed on the results of our study. All of the tests compare distributions associated with our study results for human-human vs. human-copilot pair programming. We consider a p-value of less than 0.05 to indicate a statistically significant difference in the tested distributions.

- *episode frequency*
    - Welch's t-test on episode length - $p<0.01$
- *episode length and depth*
    - Mann-Whitney U test on episode lengths - $p<0.01$
    - Mann-Whitney U test on episode depths - $p=0.67$
- *topics*
    - Chi-squared tests:
        - Overall topic distribution - $p<0.01$
        - "Tool" vs. other topics - $p=0.16$
        - "Program" vs. other topics - $p<0.01$
        - "Bug" vs. other topics - $p=0.63$
        - "Code" vs. other topics - $p<0.01$
        - "Domain" vs. other topics - $p=0.02$
        - "Technique" vs. other topics - $p=0.71$
- *finish types*
    - Chi-squared tests:
        - Overall finish type distribution - $p<0.01$
        - "Assimilation" vs. other finish types - $p=0.52$
        - "Trust" vs. other finish types - $p<0.01$
        - "Unnecessary" vs. other finish types - $p=0.38$
        - "Lost sight" vs. other finish types - $p<0.01$
        - "Gave up" vs. other finish types - $p=0.86$
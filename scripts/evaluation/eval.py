import click
import colorama

import aggregate
import questionnaire
import stats
import util

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enables verbose mode.', default=False)
def main(verbose):
    util.VERBOSE = verbose
    colorama.init()


@main.command()
@click.option('--in-path', '-i', help='Path to the file to be evaluated.', required=True,
              type=click.Path(exists=True),
              default='../transcripts/final')
@click.option('--out-path', '-o', help='Path to the output file.',
              type=click.Path(exists=False),
              default='../../results/agg')
def agg(in_path, out_path):
    aggregate.aggregate(in_path, out_path)


@main.command()
@click.option('--in-path', '-i', help='Path to the file to be evaluated.', required=True,
              type=click.Path(exists=True),
              default="../..")
@click.option('--out-path', '-o', help='Path to the output file.',
              type=click.Path(exists=False),
              default='../../results')
def quest(in_path, out_path):
    questionnaire.questionnaire(in_path, out_path)


@main.command()
@click.option('--in-path', '-i', help='Path to the file to be evaluated.', required=True,
              type=click.Path(exists=True),
              default='../../results/agg')
@click.option('--out-path', '-o', help='Path to the output file.',
              type=click.Path(exists=False),
              default='../../results')
def episode_frequency(in_path, out_path):
    stats.eval_episode_frequency(in_path, out_path)


@main.command()
@click.option('--in-path', '-i', help='Path to the file to be evaluated.', required=True,
              type=click.Path(exists=True),
              default='../../results/agg')
@click.option('--out-path', '-o', help='Path to the output file.',
              type=click.Path(exists=False),
              default='../../results')
def episode_length_depth(in_path, out_path):
    stats.eval_episode_length_depth(in_path, out_path)


@main.command()
@click.option('--in-path', '-i', help='Path to the file to be evaluated.', required=True,
              type=click.Path(exists=True),
              default='../../results/agg')
@click.option('--out-path', '-o', help='Path to the output file.',
              type=click.Path(exists=False),
              default='../../results')
def topics(in_path, out_path):
    stats.eval_topics(in_path, out_path)


@main.command()
@click.option('--in-path', '-i', help='Path to the file to be evaluated.', required=True,
              type=click.Path(exists=True),
              default='../../results/agg')
@click.option('--out-path', '-o', help='Path to the output file.',
              type=click.Path(exists=False),
              default='../../results')
def finish_types(in_path, out_path):
    stats.eval_finish_types(in_path, out_path)

if __name__ == '__main__':
    main()
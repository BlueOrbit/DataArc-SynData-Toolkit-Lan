import click
from dotenv import load_dotenv

from .pipeline import Pipeline
from .configs.config import SDGSConfig

# Load environment variables from .env file
load_dotenv()


def transform_arguments_to_configurations(
    seed: int | None, 
    output_dir: str | None, 
    export_format: str | None, 
    # task settings
    task_type: str | None, 
    task_definition: str | None, 
    # generator settings:
    generator_provider: str | None, 
    generator_model: str | None, 
) -> SDGSConfig:
    """
    Transform the optional arguments to the configuration dictionary.
    If you want to add more arguments, please add to the output config according to the following formats:
    {
        "seed": 2024,
        "output_dir": "./outputs/gsm8k",
        "export_format": "jsonl",
        "task": {
            "name": "gsm8k",
            "domain": "mathematics",
            "demo_examples_path": "./data/demo_examples",
            "task_type": "local",
            "local": {
                "parsing": {
                    "document_dir": "./dataset/documents",
                    "method": "mineru",
                    "device": "cuda:0"
                },
                "retrieval": {
                    "passages_dir": "./data/passages/wiki",
                    "method": "bm25",
                    "top_k": 10000
                },
                "generation": {
                    "task_instruction": "Generate a grade school math word problem that requires multi-step reasoning.\nThe problem should involve basic arithmetic operations and have a clear numerical answer.\n",
                    "input_instruction": "Solve the following math problem step by step. Show your work.\n",
                    "output_instruction": "Let's think step by step.\n",
                    "answer_extraction": "\"Output your final answer after ####.\"\n",
                    "num_samples": 50,
                    "temperature": 1.0
                }
            },
            "web": {
                "huggingface_token": "hf_",
                "task_instruction": "You are given a word problem involving basic arithmetic, algebra, or geometry. Your task is to carefully read the problem and provide a step-by-step solution for it.\n",
                "input_instruction": "Follow this format: Read the questions and answers carefully, and choose the one you think is appropriate among the three options A, B and C.’ then Q:[Your question here] CHOICES: A: ...,B: ...,C: ...\n",
                "output_instruction": "Your output thinking process and answer should be enclosed within <think> </think> and <answer> </answer> tags, respectively, i.e., <think> thinking process here </think> <answer> a single option here </answer>.\n  \n"
            }
        },
        "base_model": {
            "path": "./models/Qwen2.5-7B",
            "device": "cuda:0",
            "inference": {
                "temperature": 0.0,
                "max_tokens": 1500,
                "top_p": 0.95,
                "n": 1
            },
            "scoring": {
                "temperature": 1.2,
                "n": 64
            }
        },
        "llm": {
            "provider": "openai",
            "model": "gpt-4o-mini"
        },
        "answer_extraction": {
            "tag": "<answer>",
            "instruction": "Output your final answer after <answer>"
        },
        "postprocess": {
            "methods": [
                "majority_voting"
            ],
            "majority_voting": {
                "n": 16,
                "method": "exact_match",
                "exact_match": {
                    "numeric_tolerance": "1e-3"
                }
            }
        },
        "evaluation": {
            "batch_size": 100,
            "answer_comparison": {
                "method": "exact_match",
                "exact_match": {
                    "numeric_tolerance": "1e-3"
                }
            }
        },
        "rewrite": {
            "method": "difficulty_ajust",
            "input_instruction": "Solve the following math problem step by step. Show your work.\n",
            "output_instruction": "Let's think step by step.\n",
            "difficulty_adjust": {
                "easier_temperature": 0.9,
                "harder_temperature": 1.1
            }
        }
    }
    """
    config = {}
    # global settings
    if seed:
        config["seed"] = seed
    if output_dir:
        config["output_dir"] = output_dir
    if export_format:
        config["export_format"] = export_format
    # task
    task_config = {}
    if task_type:
        task_config["task_type"] = task_type
    if task_definition:
        for t in ["local", "web"]:
            if t == "local":
                task_config[t] = {"generation": {"task_instruction": task_definition}}
            else:
                task_config[t] = {"task_instruction": task_definition}

    # generator
    llm_config = {}
    if generator_provider:
        llm_config["provider"] = generator_provider
    if generator_model:
        llm_config["model"] = generator_model

    # integrate
    if task_config:
        config["task"] = task_config
    if llm_config:
        config["llm"] = llm_config
    return config


@click.command()
@click.argument("config_file", type=click.Path(exists=True), required=False)
@click.option("--seed", type=int, help="Random seed for reproducibility")
@click.option("--output_dir", type=str, help="Output directory for generated data")
@click.option("--export_format", type=str, help="Export format (jsonl, json, csv)")
@click.option("--task_type", type=str, help="Task type (local, web, distill)")
@click.option("--task_definition", type=str, help="Task definition/instruction")
@click.option("--generator_provider", type=str, help="LLM provider for generator (e.g., openai, ollama)")
@click.option("--generator_model", type=str, help="LLM model name for generator")
def generate(
    config_file: str | None,
    seed: int | None,
    output_dir: str | None,
    export_format: str | None,
    # task settings
    task_type: str | None,
    task_definition: str | None,
    # generator settings:
    generator_provider: str | None,
    generator_model: str | None,
) -> None:
    """Generate training data from a YAML configuration file or CLI parameters."""
    # process configuration from a YAML file.
    config = SDGSConfig.from_yaml(config_file)

    # process additional options
    config.update(transform_arguments_to_configurations(
        seed, 
        output_dir, 
        export_format, 
        # task settings
        task_type, 
        task_definition, 
        # generator settings:
        generator_provider, 
        generator_model, 
    ))

    # run pipeline to get data
    pipeline = Pipeline(config)
    pipeline.run()


if __name__ == "__main__":
    generate()
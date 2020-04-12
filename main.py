"""
Main script for running mentor matching
"""
import logging

from mentor_matching.cli import run

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()

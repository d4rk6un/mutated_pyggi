"""
Improving non-functional properties ::
"""
import sys
import os
import random
import argparse
import re
from pyggi.tree import TreeProgram, StmtReplacement, StmtInsertion, StmtDeletion, VariableReplacement, CmpOperReplacement
from pyggi.algorithms import LocalSearch

class MyXMLProgram(TreeProgram):
    def setup(self):
        if not os.path.exists(os.path.join(self.tmp_path, "Triangle.java.xml")):
            self.exec_cmd("srcml Triangle.java -o Triangle.java.xml", path=self.path)

class MyLocalSearch(LocalSearch):
    def get_neighbour(self, patch):
        if len(patch) > 0 and random.random() < 0.5:
            patch.remove(random.randrange(0, len(patch)))
        else:
            #edit_operator = random.choice([StmtReplacement, StmtInsertion, StmtDeletion, VariableReplacement, CmpOperReplacement])
            edit_operator = random.choice([VariableReplacement, CmpOperReplacement])
            patch.add(edit_operator.create(program))
        return patch

    def stopping_criterion(self, iter, fitness):
        return fitness < 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvement Example')
    parser.add_argument('--project_path', type=str, default='../sample/Triangle_bug_java')
    parser.add_argument('--epoch', type=int, default=10,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations per epoch(default: 100)')
    args = parser.parse_args()

    program = MyXMLProgram(args.project_path)
    local_search = MyLocalSearch(program)
    result = local_search.run(warmup_reps=5, epoch=args.epoch, max_iter=args.iter, timeout=15)
    print("======================RESULT======================")

    for epoch in range(len(result)):
        if result[epoch]['Success'] == True:
            print("Epoch {}".format(epoch+1))
            print(result[epoch])
            print(result[epoch]['BestPatch'])
            print(result[epoch]['diff'])

    program.remove_tmp_variant()
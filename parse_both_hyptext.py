import time
import sys
from edit_distance import SequenceMatcher

args = sys.argv[1:]
def colored(text, c):
	return text

def print_diff(seq1, seq2, prefix1='', prefix2='', suffix1=None, suffix2=None):
    """Given a sequence matcher and the two sequences, print a Sphinx-style
    'diff' off the two."""
    ref_tokens = []
    hyp_tokens = []
    sm = SequenceMatcher(a=seq1, b=seq2)
    opcodes = sm.get_opcodes()
    for tag, i1, i2, j1, j2 in opcodes:
        # If they are equal, do nothing except lowercase them
        if tag == 'equal':
            for i in range(i1, i2):
                ref_tokens.append(seq1[i].lower())
            for i in range(j1, j2):
                hyp_tokens.append(seq2[i].lower())
        # For insertions and deletions, put a filler of '***' on the other one, and
        # make the other all caps
        elif tag == 'delete':
            for i in range(i1, i2):
                ref_token = colored(seq1[i].upper(), 'red')
                ref_tokens.append(ref_token)
            for i in range(i1, i2):
                hyp_token = colored('*' * len(seq1[i]), 'red')
                hyp_tokens.append(hyp_token)
        elif tag == 'insert':
            for i in range(j1, j2):
                ref_token = colored('*' * len(seq2[i]), 'red')
                ref_tokens.append(ref_token)
            for i in range(j1, j2):
                hyp_token = colored(seq2[i].upper(), 'red')
                hyp_tokens.append(hyp_token)
        # More complicated logic for a substitution
        elif tag == 'replace':
            seq1_len = i2 - i1
            seq2_len = j2 - j1
            # Get a list of tokens for each
            s1 = list(map(str.upper, seq1[i1:i2]))
            s2 = list(map(str.upper, seq2[j1:j2]))
            # Pad the two lists with False values to get them to the same length
            if seq1_len > seq2_len:
                for i in range(0, seq1_len - seq2_len):
                    s2.append(False)
            if seq1_len < seq2_len:
                for i in range(0, seq2_len - seq1_len):
                    s1.append(False)
            assert len(s1) == len(s2)
            # Pair up words with their substitutions, or fillers
            for i in range(0, len(s1)):
                w1 = s1[i]
                w2 = s2[i]
                # If we have two words, make them the same length
                if w1 and w2:
                    if len(w1) > len(w2):
                        s2[i] = w2 + ' ' * (len(w1) - len(w2))
                    elif len(w1) < len(w2):
                        s1[i] = w1 + ' ' * (len(w2) - len(w1))
                # Otherwise, create an empty filler word of the right width
                if not w1:
                    s1[i] = '*' * len(w2)
                if not w2:
                    s2[i] = '*' * len(w1)
            s1 = map(lambda x: colored(x, 'red'), s1)
            s2 = map(lambda x: colored(x, 'red'), s2)
            ref_tokens += s1
            hyp_tokens += s2
    if prefix1: ref_tokens.insert(0, prefix1)
    if prefix2: hyp_tokens.insert(0, prefix2)
    if suffix1: ref_tokens.append(suffix1)
    if suffix2: hyp_tokens.append(suffix2)
    print(' '.join(ref_tokens))
    print(' '.join(hyp_tokens))


hyp_file1 =  args[1]
hyp_file2 =  args[2]
hyp1 = open(hyp_file1).readlines()
hyp2 = open(hyp_file2).readlines()
last_time='0'
isTimestamp = int(args[0])
if isTimestamp is None:
	isTimestamp = 0
for l1,l2 in zip(hyp1,hyp2):
	filename = l1.split()[0]
	frame = filename.split('-')[2]
	timestamp = time.strftime('%H:%M:%S', time.gmtime(int(frame)*30/1000))
	if isTimestamp == 1:
		print(last_time + ' --> ' + timestamp)
		ref=' '.join(l1.split()[1:])
		hyp=' '.join(l2.split()[1:])
		ref = list(map(str.lower, ref.split()))
		hyp = list(map(str.lower, hyp.split()))
		print_diff(ref,hyp)
	else:
		print(' '.join(l1.split()[1:]), end='')
		print(' ', end='')
	last_time = timestamp
	

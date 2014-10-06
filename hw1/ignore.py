from limerick import LimerickDetector

ld = LimerickDetector()
print ld.num_syllables("dog")
print ld.rhymes("dog", "bog")
print ld.guess_syllables("splorkatuk")
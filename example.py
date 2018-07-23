import os

import StROBe.Corpus.feeder as fee
import StROBe.Corpus.residential as res
cleanup = True

strobeDir = os.getcwd()
# Test Household.parametrize() and .simulate()
family = res.Household("Example family")
family.parameterize()
family.simulate()

# Test feeder
fee.IDEAS_Feeder('Example', 5, strobeDir)

# cleanup
if cleanup:
    for file in os.listdir(strobeDir):
        print file
        if file.endswith(('.p', '.txt')):
            os.remove(os.path.join(strobeDir, file))

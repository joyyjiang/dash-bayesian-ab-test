# dash-bayesian-ab-test
This web app interprets your Bayesian AB testing result.  

## Assumptions:
1. it's built for ab testing metrics that have binary outcomes, eg conversion, retention, click-through, customer complaint etc. The metrics' underlying distribution is thus beta distribution. Beta has conjugate prior, meaning that the prior and posterior distribution are both in the beta family, with parameters alpha and beta being different.

2. it assumes no prior knowledge about the metrics. it sets prior beta distribution's parameter to be alpha=beta=1, which is called uninformative prior. This way,  we let the data fully determine the posterior distribution, without mixing our bias in the process. One disadvantage of setting uninformative prior is that it takes longer for the distribution to converge, but as we collect more data, this disadvantage will disappear.


## Input: It takes 5 values

### Control group sample size:
population in control group

### Control group's success #:
count of successful events in control group. A success is defined as making a conversion, click-through etc.

### Experiment group sample size:
population in control group

### Experiment group's success #:
count of successful events in experiment group. A success is defined as making a conversion, click-through etc.

### minimum %lift:
percent lift(%lift) is defined as percentage increase of metrics in experiment group compared to control group. Mathematically,
%lift= (experiment group success#/experiment group sample size - control group success#/control group sample size) / (control group success#/control group sample size)
minimum %lift is defaulted to zero, but can take any value between -1 and 1, based on business needs.

## Output: it outputs two graphs and one final recommendation.

The top graph shows updated beta distribution of control and experiment group, given the collected data.

The bottom graph shows the distribution of %lift. It is an arbitrary plot based on 100,000 simulations from the posterior distributions. The right side of the dotted line is the portion of the plot that exceeds the minimum % lift.

The final recommendation is based on the portion of the %lift plot.  If it exceeds 95%, the experiment group is the winner. if it is lower than 5%, control group the winner. Any value in between,  we cannot reach a conclusion yet.

Note that there's no industry standard of choosing a decision rule or setting the decision rule's threshold, since Bayesian AB testing is still fairly young.  Different people may have different methodologies.  

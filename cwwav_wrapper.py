import subprocess


def main(
    output: str,
    input: str | None = None,
    filename: str | None = None,
    stereo: bool = False,
    phaseshift = 0,
    frequency: int = 660,
    rate: int = 16_000,
    wpm: int = 25,
    farnsworth: int | None = None,
    envelope: float = 10.0
):
    command = ['cwwav']

    if stereo:
        command += ['--stereo', '--phaseshift', str(phaseshift)]

    command += ['--output', str(output)]
    command += ['--frequency', str(frequency)]
    command += ['--rate', str(rate)]
    command += ['--wpm', str(wpm)]

    if farnsworth is not None:
        command += ['--farnsworth', str(farnsworth)]

    command += ['--envelope', str(envelope)]

    kwargs = dict()
    kwargs['stdout'] = subprocess.DEVNULL
    kwargs['stderr'] = subprocess.DEVNULL

    if filename is not None:
        command += [str(filename)]

    if input is not None:
        kwargs['input'] = bytes(input, 'utf-8')

    subprocess.run(command, **kwargs)


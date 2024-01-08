"""Contains common matplotlib functionality."""
import matplotlib as mpl
import matplotlib.pyplot as plt


def setup_plot_and_axes(
    fig: mpl.figure.Figure, title: str, xlabel="Time", ylabel="Euros"
) -> None:
    """Set up the plot, axes and title for the given figure for a plot."""
    plt.title(title)
    plt.grid(color="k", linestyle="-", linewidth=0.1)
    ax = fig.axes[0]
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%b %d '%y"))
    ax.xaxis.set_major_locator(mpl.dates.MonthLocator())
    ax.xaxis.set_minor_locator(mpl.dates.WeekdayLocator(byweekday=0))
    ax.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda x, _: format(int(x), ","))
    )
    fig.autofmt_xdate()


def setup_yearly_plot_and_axes(
    fig: mpl.figure.Figure, title: str, xlabel="Time", ylabel="Euros"
) -> None:
    """Set up the plot, axes and title for the given figure for a plot."""
    plt.title(title)
    plt.grid(color="k", linestyle="-", linewidth=0.1)
    ax = fig.axes[0]
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mpl.dates.YearLocator())
    ax.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda x, _: format(int(x), ","))
    )
    plt.xticks(rotation=45)

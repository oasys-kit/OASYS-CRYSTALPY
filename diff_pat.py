
def plot_crystal_sketch(v0_h,v0_v,vH_h ,vH_v ,H_h ,H_v):

    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    import matplotlib.patches as patches

    hshift = 0.2
    vshift = 0.0

    plt.figure(1, figsize=(6,6))
    ax = plt.subplot(111)
    ax.xaxis.set_ticks_position('none)
    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_ticklabels([])
    ax.yaxis.set_ticklabels([])


    # draw axes

    plt.xlim([-2.2,2.2])
    plt.ylim([-2.2,2.2])

    ax.annotate("",
                xy    =(0.0,0.0), xycoords='data',
                xytext=(2.0,0.0), textcoords='data',
                arrowprops=dict(arrowstyle="<-",connectionstyle="arc3"),)
    plt.text(2, 0,"$x_2$", color='k')

    ax.annotate("",
                xy    =(0.0,0.0), xycoords='data',
                xytext=(0.0,2.0), textcoords='data',
                arrowprops=dict(arrowstyle="<-",connectionstyle="arc3"),)
    plt.text(0, 2,"$x_3$", color='k')


    # draw vectors

    ax.annotate("",
                xy    =(-v0_h,-v0_v), xycoords='data',
                xytext=(0.0,0.0), textcoords='data',
                arrowprops=dict(arrowstyle="<-",connectionstyle="arc3",color='red'),)
    plt.text(-v0_h+hshift,-v0_v+vshift, r"$\vec k_0$", color='r')


    ax.annotate("",
                xy    =(0,0), xycoords='data',
                xytext=(vH_h,vH_v), textcoords='data',
                arrowprops=dict(arrowstyle="<-",connectionstyle="arc3",color='red'),)
    plt.text(vH_h+hshift,vH_v+vshift, r"$\vec k_H$", color='r')


    ax.annotate("",
                xy    =(0,0), xycoords='data',
                xytext=(H_h,H_v), textcoords='data',
                arrowprops=dict(arrowstyle="<-",connectionstyle="arc3",color='blue'),)
    plt.text(H_h+hshift,H_v+vshift, r"$\vec H$", color='b')


    # draw Bragg plane

    ax.annotate("",
                xy    =(0,0), xycoords='data',
                xytext=( -H_v*1.5, H_h*1.5), textcoords='data',
                arrowprops=dict(arrowstyle="-",connectionstyle="arc3",color='green'),)

    ax.annotate("",
                xy    =(0,0), xycoords='data',
                xytext=(H_v*1.5,-H_h*1.5), textcoords='data',
                arrowprops=dict(arrowstyle="-",connectionstyle="arc3",color='green'),)

    # draw crystal
    #
    x1 = -0.8
    y1 = -0.1
    x2 =  0.8
    y2 =  0.0

    verts = [
        (x1,y1), # left, bottom
        (x2,y1), # left, top
        (x2,y2), # right, top
        (x1,y2), # right, bottom
        (x1,y1), # ignored
        ]


    codes = [Path.MOVETO,
             Path.LINETO,
             Path.LINETO,
             Path.LINETO,
             Path.CLOSEPOLY,
             ]

    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='orange', lw=2)
    ax.add_patch(patch)

    plt.show()



if __name__ == "__main__":

    # All vectors are normalized

    v0_h =   0.92515270745695932
    v0_v =  -0.37959513680375029
    vH_h =   0.99394445110430663
    vH_v =   0.10988370269953050
    H_h =   0.13917309988899462
    H_v =   0.99026806889209951

    plot_crystal_sketch(v0_h,v0_v,vH_h ,vH_v ,H_h ,H_v)



